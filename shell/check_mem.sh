#!/usr/local/bin/zsh

program="python2 /usr/local_qa/bin/pq_stress.py"

max=0
last_res=0
last_max=0
last_fds=0

calc_mem(){
pid=`pgrep -f $program`

if [ ! -n "$pid" ]; then
return
fi

res=`ps -aux -p $pid | grep root | cut -w -f 5`
thread=`ps -o nlwp $pid | tail -1`
thread=`echo $thread | tr -d ' '`
date=`date`

if [ ! -n "$res" ]; then
return
fi

#echo "pid, res, max = $pid, $res, $max"
if [ $res -gt $max ] ; then
  max=$res
fi

if [ $last_res -ne $res ] || [ $last_max -ne $max ]; then
echo "$date  $res, $max pid=$pid threads=$thread"
echo "$date  $res, $max pid=$pid threads=$thread" >> /var/log/evers_debug.log
last_res=$res
last_max=$max
fi

}

while true
do
    calc_mem
    sleep 1
done

