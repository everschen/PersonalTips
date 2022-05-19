#!/bin/bash

#source ../build/envsetup.sh
#c4dev@sles15-everschen-dev-00:~> ./execute_cmd_in_sp.sh 10.229.34.42 "cat /etc/pramfs/c4_safe_ktrace.log"



if [ ! -n "$1" ] ;then
    echo "Please input array ip!"
    exit 0
fi

if [ ! -n "$2" ] ;then
    echo "Please input cmd!"
    exit 0
fi



ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$1 $2 2>/dev/null


