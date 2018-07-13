#!/bin/sh

# Kill libvirtd
killall libvirtd
systemctl daemon-reload
systemctl restart libvirtd

virsh destroy vm3
rmdir /sys/fs/resctrl/mon_groups/*
virsh start vm3

NUM_LIBVIRTD=$(ps axu|grep libvirtd | awk '/\/usr\/sbin\/libvirtd/ {print $2}' |wc -l)
PID_LIBVIRTD=$(ps aux|grep libvirtd | awk '/\/usr\/sbin\/libvirtd/ {print $2}')

if [ $NUM_LIBVIRTD != 1 ]; then
    echo "Too many libvirtd process, exit"
    echo "libvirtd process count: $NUM_LIBVIRTD"
fi

echo $PID_LIBVIRTD
gdb -x command.gdb /usr/sbin/libvirtd $PID_LIBVIRTD 
#gdb /usr/sbin/libvirtd $PID_LIBVIRTD 
