#!/bin/bash

wait_for_ten_min=600
wait_start=0

action=$1
function trap_ctrlc ()
{
    # perform cleanup here
    echo "Ctrl-C caught...performing clean up"
	./evers_control.sh stop
    echo "Doing cleanup"

    # exit shell script with error code 2
    # if omitted, shell script will continue execution
    exit 2
}

trap trap_ctrlc INT


if [[ "$action" == "start" ]]; then
    pid=`ps -ef |grep evers.sh |grep -v grep|awk '{print $2}'`	
	if [[ "$pid" ]]; then
		echo "evers.sh is running, pid is $pid"
		bpid=`ps -ef |grep "bminer -uri" |grep -v grep|awk '{print $2}'`
		bbpid=(`echo $bpid| tr '\n' ' '`)	
		if [[ "$bpid" ]]; then
			echo "bminer is running, pid is ${bbpid[0]}, ${bbpid[1]}"
			echo "no need to start it again!!!"
		else
			echo "stop the process $pid"
			kill -9 $pid
			echo "/home/evers/bminer/evers.sh"
			/home/evers/bminer/evers.sh&
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
		echo "/home/evers/bminer/evers.sh"
		/home/evers/bminer/evers.sh&
	fi
	

elif [[ "$action" == "stop" ]]; then
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


while :
do
    echo "============================================================================="
	pid=`ps -ef |grep evers.sh |grep -v grep|awk '{print $2}'`
	if [[ -z "$pid" ]]; then
		echo "evers.sh is not running"
		if [ $wait_start -ne 0 ]; then
			current_time=`date +%s`
			wait=`expr $current_time - $wait_start`
			echo "wait time is $wait"
			
			if [ $wait -gt $wait_for_ten_min ]; then
				./evers_control.sh start
				wait_start=0
			else
				echo "sleep 5 seconds more"
				sleep 5
			fi
		else
			wait_start=`date +%s`
			sleep 2
		fi
	else
		echo "evers.sh is running, pid is $pid"		
		bpid=`ps -ef |grep "bminer -uri" |grep -v grep|awk '{print $2}'`
		bbpid=(`echo $bpid| tr '\n' ' '`)	
		if [[ -z "$bpid" ]]; then
			echo "bminer is not running"
			./evers_control.sh start
			wait_start=0
		else
			echo "bminer is running, pid is ${bbpid[0]}, ${bbpid[1]}"
			sleep 30
		fi
	fi
done





