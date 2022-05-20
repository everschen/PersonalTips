#!/usr/bin/python3

import re
import os
import sys


argnum = len(sys.argv)
arg_tmp=""

if argnum == 2:
    arg_tmp = sys.argv[1]
total_income = 0
total_str = ""
first_one = True
command_str = "./check_today_order.sh "
command_str += arg_tmp
command_str +=" | grep SELL"

result = os.popen(command_str)
res = result.read()
print(res)
for line in res.splitlines():  
    #print line
    result = re.search(r"""[0-9]+(\.[0-9]{1,2})?$""", line)
    #print(result.group())
    total_income += float(result.group())
    if first_one:
        total_str += result.group()
        first_one = False
    else:
        total_str += " + " + result.group()
print("%s = %.2f"%(total_str, total_income))
#str="2021-06-07 05:34:06 eth3lusdt SELL done: 21.7969 buy:21.3441 diff:0.4528 amount=23.3788 income=67.6"