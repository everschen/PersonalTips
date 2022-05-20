#!/bin/sh
filename=`ls log/auto-hunter-trade-done* -t |head -n1|awk '{print $0}'`
echo "tail -f $filename"
tail -f $filename
