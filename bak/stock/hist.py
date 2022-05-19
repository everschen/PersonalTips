# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 00:29:31 2015

@author: Administrator
"""
import tushare as ts
df = ts.get_hist_data('600100')
#df = ts.get_today_ticks(code)
print df