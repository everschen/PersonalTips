#!/bin/bash

if [[ "$1" == "start" ]]; then
    pid=`ps -ef |grep evers.sh |grep -v grep|awk '{print $2}'`	
	if [[ "$pid" ]]; then
		echo "evers.sh is running, pid is $pid"
		bpid=`ps -ef |grep "bminer -uri" |grep -v grep|awk '{print $2}'`
		bbpid=(`echo $bpid| tr '\n' ' '`)	
		if [[ "$bpid" ]]; then
			echo "bminer is running, pid is ${bbpid[0]}, ${bbpid[1]}"
			echo "no need to start it again!!!"
			exit 1
		else
			echo "stop the process $pid"
			kill -9 $pid
		fi
	else
		bpid=`ps -ef |grep "bminer -uri" |grep -v grep|awk '{print $2}'`
		bbpid=(`echo $bpid| tr '\n' ' '`)	
		if [[ "$bpid" ]]; then
			echo "bminer is running, pid is ${bbpid[0]}, ${bbpid[1]}"
			echo "stop the process ${bbpid[0]}"
			kill -9 ${bbpid[0]}
			echo "stop the process ${bbpid[1]}"
			kill -9 ${bbpid[1]}
		fi	
	fi
	
    echo "/home/evers/bminer/evers.sh"
    /home/evers/bminer/evers.sh&

elif [[ "$1" == "stop" ]]; then
    pid=`ps -ef |grep evers.sh |grep -v grep|awk '{print $2}'`	
	if [[ -z "$pid" ]]; then
		echo "evers.sh is not running"
	else
		echo "evers.sh is running, pid is $pid"
		echo "stop the process $pid"
		kill -9 $pid
	fi
	
	bpid=`ps -ef |grep "bminer -uri" |grep -v grep|awk '{print $2}'`
	bbpid=(`echo $bpid| tr '\n' ' '`)	
	if [[ -z "$bpid" ]]; then
		echo "bminer is not running"
	else
		echo "bminer is running, pid is ${bbpid[0]}, ${bbpid[1]}"
		echo "stop the process ${bbpid[0]}"
		kill -9 ${bbpid[0]}
		echo "stop the process ${bbpid[1]}"
		kill -9 ${bbpid[1]}
	fi

    pid=`ps -ef |grep evers_monitor.sh |grep -v grep|awk '{print $2}'`	
	if [[ -z "$pid" ]]; then
		echo "evers_monitor.sh is not running"
	else
		echo "evers_monitor.sh is running, pid is $pid"
		echo "stop the process $pid"
		kill -9 $pid
	fi

else
    pid=`ps -ef |grep evers.sh |grep -v grep|awk '{print $2}'`
	if [[ -z "$pid" ]]; then
		echo "evers.sh is not running"
	else
		echo "evers.sh is running, pid is $pid"		
	fi
	
	bpid=`ps -ef |grep "bminer -uri" |grep -v grep|awk '{print $2}'`
	bbpid=(`echo $bpid| tr '\n' ' '`)	
	if [[ -z "$bpid" ]]; then
		echo "bminer is not running"
	else
		echo "bminer is running, pid is ${bbpid[0]}, ${bbpid[1]}"		
	fi
fi