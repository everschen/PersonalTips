#!/bin/sh
if [ -n "$1" ]; then
    num=$1
else
    num=0
fi

cur_date=`date +"%Y-%m-%d" -d  "-$num days"`
#echo $cur_date
grep -rh $cur_date log/* | grep -e "SELL done" -e "BUY done"
#grep -rn $cur_date log/* | grep "done"
