#!/bin/bash


logfile="/tmp/evers_debug.log"

date=`date`
echo "start to monitor ntp issue"
echo "$date  \n start to monitor ntp issue" >> $logfile
threshold=500.0

calc_mem(){
date=`date`;
echo "$date checking the offset values start ..."

new_vlaue=`/usr/bin/isi_for_array -s ntpq -np | awk '{print $1,$2, $10}'`
time_vlaue=`/usr/bin/isi_for_array -s date`
offsets=`/usr/bin/isi_for_array -s ntpq -np | awk '{print $10}'`


offset=(`echo $offsets| tr '\n' ' '`)

for(( i=0;i<${#offset[@]};i++));
do
    if [ ${offset[i]} == "offset" ] || [ ${offset[i]} == "" ]; then
        #echo "${offset[i]} continue";
        continue;
    fi

    #echo ${offset[i]};
    a=${offset[i]}
    a=${a#-}
    a=${a#+}
    echo "offset abs: $a"

    if (( $(echo "$a > $threshold" |bc -l) )); then
        echo "${offset[i]} gt";
        date=`date`;
        echo "$date";
        echo "$new_vlaue";
        echo "$time_vlaue";
        echo "$date" >> $logfile;
        echo "$new_vlaue" >> $logfile;
        echo "$time_vlaue" >> $logfile;
        echo "" >> $logfile;
        echo "";
        return
    fi
done;

}

while true
do
    calc_mem
    sleep 1
done

