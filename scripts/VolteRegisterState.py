# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:57:59 2016

@author: evers.chen
"""
import sys  
import glob  
import os  
import datetime

	
class item:
	def __init__(self):
		self.source = ''     
		self.time = 0    
		self.value = ''     


last = item()
last.source = ""
last.value = ""
currenttime = '01-01 12:09:31'
d1 = datetime.datetime.strptime(currenttime, '%m-%d %H:%M:%S')
last.time = d1		
	
def behindstr(source, pattern):
	#print source
	#print pattern
	pos1 = source.index(pattern)

	if pos1 == -1:
		print "not found pattern"
		return ""
	match='\n'
	pos2 = source.find(match,pos1)
	ret = source[pos1 + len(pattern):pos2]
	return ret

			
			
def add_line_to_file(title, filename, insert):
    str_len=18
    with open(filename, 'a+') as f:
        fff=open(filename)
        ff=fff.read()
        pos1 = ff.find(title)
        if pos1 != -1:
            return
			
    	lines = f.readlines()
    	#print "len="+str(len(lines))
    	#print lines
    	if len(lines) == 0 :
    		file_object = open(filename, 'a+')
    		file_object.write(title)
    		file_object.close()
    		return
			
    	if insert == 0 :			
    		file_object = open(filename, 'a+')
    		file_object.write(title)
    		file_object.close()		
    		return
		
    	for i in range(0, len(lines)):
    		#print "i="+str(i)
    		#print "p1:"+lines[i]
    		#print "p2:"+lines[i][0:str_len]
    		#print "p3:"+title[0:str_len]
    		if cmp(lines[i][0:str_len],title[0:str_len]) > 0 :
    			#print "pos2"
    			lines[i:1] = [title]
    			open(filename, 'w').writelines(lines)
    			return
    		else:
    			#print "pos1"
    			continue

		
    	#print len(lines),i
    	if len(lines)-1 == i :
    		#print len(lines),i
    		file_object = open(filename, 'a+')
    		file_object.write(title)
    		file_object.close()
    		return				
				
		#open(cfg_sa, 'w').writelines(lines)
           
  
def checknullvalue(source, pattern):
	if pattern in source:
		ret=behindstr(source, pattern)
		if ret == "" :
			#print 'WARNING: '+ pattern + ret
			add_line_to_file(source,'system_warning.txt', 0)
			add_line_to_file(source,'system_behavior.txt', 1)
		else:
			print pattern+ret

def checkhasstring(source, pattern):
	if pattern in source:
		#print 'WARNING: '+ pattern
		add_line_to_file(source,'VolteRegisterState.txt', 0)




			
def outputKey(filename):
    f=open(filename)
    title=f.readline(2048)
    while(title):
		

		checkhasstring(title, 'ImsServiceImpl: getIMSRegAddress mImsRegAddress')
		checkhasstring(title, 'SECURITY IKE: INFO: Attribute: INTERNAL_IP6_ADDRESS')
		checkhasstring(title, 'SECURITY IKE: INFO: Attribute: INTERNAL_IP4_ADDRESS')
		checkhasstring(title, 'IMSREGADDR')
		checkhasstring(title, 'AT+IMSHO')
		checkhasstring(title, 'AT+VOWIFIEN=0')
		checkhasstring(title, 'AT+IMSWFATT=')
		checkhasstring(title, 'AT+VOWFREG')		
		checkhasstring(title, 'CGEV: NW PDN DEACT')
		checkhasstring(title, 'CGEV: NW ACT')
		checkhasstring(title, 'Update the call state to data router')
		checkhasstring(title, 'startVoWifiCall')
		checkhasstring(title, 'EVENT_WIFI_ALL_CALLS_END')
		checkhasstring(title, 'setIMSRegAddress')
		checkhasstring(title, 'startVoLteCall')
		checkhasstring(title, 'startVoWifiCall')
		checkhasstring(title, 'VolteRegisterState')
		checkhasstring(title, '^CONN')
		checkhasstring(title, 'CIREG')
		checkhasstring(title, 'startVoLteCall')
		checkhasstring(title, 'startVoLteCall')

		
		
		title=f.readline(2048)
    f.close()
 

    
       
        

dir = 'E:\\LOG\\20160318-135756'  
dir = './'  
suffix = 'txt'  


f = glob.glob(dir + '\\system_behavior.' + suffix)  
#print f 


for file in f :  
    filename = os.path.basename(file)  
    print file
    outputKey(file)        
    

