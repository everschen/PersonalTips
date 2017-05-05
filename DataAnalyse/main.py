# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 2017

@author: evers.chen
"""

import glob,datetime,re
import ConfigParser
import string, os, sys
sys.path.append('./register') 
import utilities

FIND_PATTERN = False
 
cf = ConfigParser.ConfigParser()
cf.read(sys.path[0]+"\config.conf")
#cf.read("test.conf")
secs = cf.sections()
print 'Sections:', secs
print ""

for section in secs :
	utilities.remove_output(cf, section)

#need to include all the filter from other sections
utilities.handle_main_section(cf)

for section in secs :
	if section == 'main':
		continue
	print 'Process section',section, '...'
	utilities.handle_section(cf, section)
	print ""
	



