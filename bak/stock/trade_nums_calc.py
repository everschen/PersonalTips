# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tushare as ts

#ts.get_hist_data('300075')

#df = ts.get_hist_data('300075',start='2015-07-01',end='2015-08-09')
#print df.head(10)
df = ts.get_hist_data('300075')
#print df

ret=(df[['high','low']])

print ret





  
#print df
