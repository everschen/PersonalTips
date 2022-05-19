#!/bin/bash

#source ../build/envsetup.sh

first_spa="10.207.49.5"
first_spb="10.207.49.6"

second_spa="10.229.116.43"
second_spb="10.229.116.44"

if [ ! -n "$1" ] ;then
    echo "Please input sim env 1 or 2!"
    exit 0
fi

if [ $1 -eq 1 ]; then
    spa=$first_spa
    spb=$first_spb
elif [ $1 -eq 2 ]; then
    spa=$second_spa
    spb=$second_spb
else
    echo "Please input sim env 1 or 2!"
    exit 0
fi

ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$spa pidof ECOM &> /dev/null

if [ $? -eq 0 ]; then
    echo "login to spa..."
    #print version info goshawk or ese?
    ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$spa cat /.version 2> /dev/null
    ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$spa ls /EMC/CEM/log/ese &> /dev/null
    if [ $? -eq 0 ]; then
        echo "It's ESE release!"
    else
        echo "It's GOSHAWK release!"
    fi
    ssh root@$spa
else
    ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$spb pidof ECOM &> /dev/null
    if [ $? -eq 0 ]; then
        echo "login to spb..."
        ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$spa cat /.version 2> /dev/null
        ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$spa ls /EMC/CEM/log/ese &> /dev/null
        if [ $? -eq 0 ]; then
            echo "It's ESE release!"
        else
            echo "It's GOSHAWK release!"
        fi
        ssh root@$spb
    else
        echo "Failed to login sim $1 : $spa and $spb, please have a check!"
    fi
fi
