import sys
import gdb
import os
import re

from pprint import pprint

class RunUntilCommand(gdb.Command):
    """Run until breakpoint and temporary disable other ones"""

    def __init__ (self):
        super(RunUntilCommand, self).__init__ ("run-until",
                                               gdb.COMMAND_BREAKPOINTS)

    def invoke(self, bp_num, from_tty):
        try:
            bp_num = int(bp_num)
        except (TypeError, ValueError):
            print "Enter breakpoint number as argument."
            return

        all_breakpoints = gdb.breakpoints() or []
        breakpoints = [b for b in all_breakpoints
                       if b.is_valid() and b.enabled and b.number != bp_num and
                       b.visible == gdb.BP_BREAKPOINT]

        for b in breakpoints:
            b.enabled = False

        gdb.execute("run")

        for b in breakpoints:
            b.enabled = True

def break_handler(e):
    if not isinstance(e, gdb.BreakpointEvent):
        return

    if e.breakpoint.number == 1:
        debug_virDomainRdtmonDefParse(e)
    if e.breakpoint.number == 2:
        debug_qemuDomainSetRdtmon(e)
    if e.breakpoint.number == 3:
        debug_qemuDomainGetStatsCPUResmon(e)
    else:
        print "Unprocessed reakpoint [%d]"%e.breakpoint.number

def debug_init():
    #	RunUntilCommand()
    gdb.execute('b virDomainRdtmonDefParse')
    gdb.execute('b qemuDomainSetRdtmon')
    gdb.execute('b virDomainRdtmonDefValidate')
    gdb.events.stop.connect(break_handler)

class LineInterest:
    line=''
    forced=False
    count=0
    def __init__(self, l, f, c):
        self.line = l
        self.forced = f
        self.count = c
        
def stopAtLine( line, interests):
    """
    Call until target 'line' reached.
    A list of interesting path will be checked. 
    (line, forced, count)
    :param line: 
    :param interests: array of (line, forced, count)
    :return: True for both target line reached and all interesting 
     lines are walked through.
    """
    MAX = 100
    c = 0
    l = ""
    print "\n --------- Looking for '%s' --------"%line
    while l.find(line) == -1:
        if interests:
            for interest in interests:
                if -1 != l.find(interest.line):
                    interest.count += 1             
        gdb.execute("next")
        l = gdb.execute("frame", to_string=True)
        c=c+1
        if c>MAX:
            print("stopAtLine[%s] failed: step exceeds limitation(100 steps)" %line)
            return False
    # check interests are satisfied or not
    ret = True;
    if interests:
        for interest in interests:
            if interest.forced and interest.count==0:
                ret = False
    if not ret:
        print "\n"
        print     "----- ----- ----  ----------------------------------------"
        for i in interests:
            if i.forced and i.count==0:
                print "-BAD- %5s%5d  %s"%(i.forced, i.count, i.line)
            else:
                print "      %5s%5d  %s"%(i.forced, i.count, i.line)
        print "\n"

    return ret
            
def debug_virDomainRdtmonDefParse(e):
    return
    """ function called at the break point of 'virDomainRdtmonDefParse'
    """
    print "\n >>>> virDomainRdtmonDefParse"
    if not stopAtLine("for (i = 0; i < n; i++)", None):
        print "!!! Error"
        return
    n = gdb.parse_and_eval("n")
    if n == 0:
        print("!!!! No 'rdtMonitoring section found")
        xmls = gdb.execute("call virXMLNodeToString(ctxt->node->doc,ctxt->node)", to_string=True)
        print(type(xmls))
        lines = xmls.split("\\n")
        print("length is ", len(lines))
        for l in lines:
            print(l)
        gdb.execute("continue")
        
    stopAtLine("virDomainRdtmonDefValidate", None)
    gdb.execute("s")

    if not stopAtLine("return", None):
        print "!!! Error"
        return

    retVal = gdb.execute("print ret", to_string=True)
    if not retVal:
        print "!!!! Error in virDomainRdtmonDefValidate"
        gdb.execute("c")
   
    if not stopAtLine("virDomainRdtmonDefAdd", None):
        print "!!! Error"
        return
    gdb.execute("s")
    interests = [LineInterest("virResctrlMonNew", True, 0),
                 LineInterest("VIR_APPEND_ELEMENT", True, 0)
                 ]
    if not stopAtLine("return", interests):
        print "!!! Error"
        return
    retVal = gdb.execute("print ret", to_string=True)
    if -1 == retVal:
        print "!!!! Error in virDomainRdtmonDefAdd"
        return
    
    print " <<<< virDomainRdtmonDefParse \n"
    gdb.execute("c")

def debug_qemuDomainGetStatsCPUResmon(e):
    print "\n >>>> qemuDomainGetStatsCPUResmon"
    interests = [ LineInterest("i < vm->def->nresmons", True, 0),
            ]

    if not stopAtLine("return", interests):
        print "!!! Error"
        return

    print "\n <<<< qemuDomainGetStatsCPUResmon"
    gdb.execute("c")
    

def debug_qemuDomainSetRdtmon(e):
    return
    print "\n >>>> qemuDomainSetRdtmon"

    interests = [ LineInterest("if (!(vm = qemuDomObjFromDomain(dom)))", True, 0),
            LineInterest("if (virDomainSetRdtmonEnsureACL(dom->conn)", True, 0),
            LineInterest("qemuDomainObjBeginJob", True, 0),
            LineInterest("virDomainObjGetDefs", True, 0),
            LineInterest("action == VIR_RESCTRL_MONACT_DISABLE", False, 0),
            LineInterest("mon = virDomainRdtmonDefAdd(def,", True, 0),
            LineInterest("virDomainRdtmonDefValidate(persistentDef", True, 0),
            LineInterest("(virDomainSaveConfig", True, 0),
            LineInterest("virResctrlMonCreate(pairedalloc", False, 0),
            LineInterest("virResctrlMonAddPID", False, 0),
            LineInterest("virResctrlMonRemove(mon)", False, 0),
            LineInterest("virDomainObjEndAPI(&vm)", True, 0)
            ]
    if not stopAtLine("return", interests):
        print "!!! Error"
        return
    retVal = gdb.execute("print ret", to_string=True)
    if -1 == retVal:
        print "!!!! Error in virDomainRdtmonDefAdd"
        return

    print "\n <<<< qenuDomainnetRdtmon"
    gdb.execute("c")
