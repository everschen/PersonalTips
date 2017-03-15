# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:57:59 2016

@author: evers.chen
"""
import sys  
import glob  
import os  
import _winreg
     
def add_line_to_file(title, filename, num):
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
    			#print "pos2"
    			continue

		
    	#print len(lines),i
    	if len(lines)-1 == i :
    		#print len(lines),i
    		file_object = open(filename, 'a+')
    		file_object.write(title)
    		file_object.close()
    		return				
				
		#open(cfg_sa, 'w').writelines(lines)
		



           
  

    
def outputKey(filename):
    num=0
    f=open(filename)
    title=f.readline(2048)
    while(title):
		if "^CONN" in title or "+CIREGU" in title or "+CIREG?" in title or "+IMSHO" in title or "+VOWFREG" in title or "+IMSWFATT" in title or "+IMSHOWFINF" in title or "+IMSHOCALLEND" in title or "+VOWIFIEN" in title:
			#print title
			add_line_to_file(title,'handover.txt', num)
		if "ImsCMUtils" in title:
			#print title
			add_line_to_file(title,'handover.txt', num)
		title=f.readline(2048)
		num=num+1
    f.close()
 

    
       
        

dir = 'E:\\LOG\\20160318-135756'  
dir = './'  
suffix = 'log'  
f = glob.glob(dir + '\\*.' + suffix)  
print f 


for file in f :  
    filename = os.path.basename(file)  
    #print file
    outputKey(file)        
    

