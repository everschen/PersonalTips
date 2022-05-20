#!/bin/sh
filename=`ls log/auto-hunter-price-big-change* -t |head -n1|awk '{print $0}'`
echo "tail -f $filename"
tail -f $filename
