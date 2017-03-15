# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:57:59 2016

@author: evers.chen
"""
import sys  
import glob  
import os  
import _winreg
     
def add_line_to_file(title, filename, insert):
    str_len=220
    with open(filename, 'a+') as f:
        fff=open(filename)
        ff=fff.read()
    	match = title[43:200]
        pos1 = ff.find(match)
    	print match
    	print match[0:15]
    	print
        if pos1 != -1:
            return
        if match[0:15] == 'Security-Server':
            title = match + '\n\n'
    	else:
			title = match + '\n'

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
    		print i,lines
    		print
    		if cmp(lines[i][45:str_len],title[45:str_len]) != 0:
    			print i,lines[i][45:str_len]
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
		



           
  

    
def outputKey(filename):
    num=0
	
    if "main" in filename:
    	insert=0
    elif "radio" in filename:
    	insert=1
    elif "charon" in filename:
    	insert=1
    	return
    elif "mtc" in filename:
    	insert=1
    	return		
    elif "system" in filename:
    	insert=1
    	return
    else:
    	insert=3
    print insert,filename

	
    f=open(filename)
    title=f.readline(2048)
    while(title):
		
		if "D LEMON   : Security-Server:" in title:
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_warning.txt', 0)
			else:
				add_line_to_file(title,'ipsecsa.txt', insert)
    			
			title=f.readline(2048)
			continue
		if "D LEMON   : Security-Client:" in title:
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_warning.txt', 0)
			else:
				add_line_to_file(title,'ipsecsa.txt', insert)
			title=f.readline(2048)
			continue		
		title=f.readline(2048)
    f.close()
 

    
       
        

dir = 'E:\\LOG\\20160318-135756'  
dir = './'  
suffix = 'log'  
f = glob.glob(dir + '\\*.' + suffix)  
print f 


for file in f :  
    filename = os.path.basename(file)  
    print file
    outputKey(file)        
    

