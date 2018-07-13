b virDomainRdtmonDefParse 
commands
b conf/domain_conf.c:19135
commands
print "no ./cputune/rdtMonitoring found"
c
end
b conf/domain_conf.c:19165
commands
printf "rdtmon[%d/%d]: vcpu string=%s, enable string=%s",i,n,vcpus_str,enable_str
c
end
finish
c
end

# 19130         goto cleanup;

b virDomainRdtmonDefAdd
commands
info args
printf ">>> def->nrdtmons = %d\n",def->nrdtmons
finish
printf ">>> def->nrdtmons = %d\n",def->nrdtmons
c
end

b virDomainRdtmonDefValidate
commands
info args
finish 
printf "paired alloc = %p", *pairedalloc
c
end

b virDomainRdtmonDefFormat
commands
finish 
c
end
