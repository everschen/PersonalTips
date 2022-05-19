# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:57:59 2016

@author: evers.chen
"""
import sys  
import glob  
import os  
import _winreg
     

os.popen('python E:/LOG/scripts/reg_ui_sys.py')
os.popen('python E:/LOG/scripts/key_build.py')
##cd ../kernel/
os.popen('python E:/LOG/scripts/parse_imsbr_file.py')
os.popen('python E:/LOG/scripts/handover_log.py')
os.popen('python E:/LOG/scripts/system_warning.py')



