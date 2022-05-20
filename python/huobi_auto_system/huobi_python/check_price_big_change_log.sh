#!/bin/sh

if [ -n "$1" ]; then
    sym=$1
else
    sym=""
fi

filename=`ls log/auto-hunter-price-big-change-$sym* -t |head -n1|awk '{print $0}'`
echo "tail -f $filename"
tail -f $filename
