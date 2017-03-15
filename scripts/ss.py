# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:57:59 2016

@author: evers.chen
"""
import sys  
import glob  
import os  
import _winreg
     

def analyse_file(file_name_filter):
	dir = './'  
	suffix = 'log'  
	f = glob.glob(dir + '\\*'+file_name_filter+'*.' + suffix)  
	for file in f :  
		filename = os.path.basename(file)  
		print file
		outputKey(file)        


		
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
    	#print insert
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

    	if insert == 99 :
    		for i in range(0, len(lines)):
    			#print "i="+str(i)
    			#print "p1:"+lines[i]
    			#print "p2:"+lines[i][0:str_len]
    			#print "p3:"+title[0:str_len]
    			tmp = lines[i][0:6] + title	
    			if cmp(lines[i][0:str_len],tmp[0:str_len]) > 0 :
    				#print "pos2"
    				lines[i:1] = [tmp]
    				open(filename, 'w').writelines(lines)
    				return
    			else:
    				#print "pos1"
    				continue			
			
    	if insert == 88 :	
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
		



           
  

    
def outputKey(filename):
    num=0
	
    if "main" in filename:
    	insert=0
    elif "radio" in filename:
    	insert=1
    elif "imsbr" in filename:
    	insert=88
    elif "mtc" in filename:
    	insert=99	
    elif "missinglog" in filename:
    	insert=77			
    elif "system" in filename:
    	insert=77
    else:
    	insert=3
    print insert,filename

	
    f=open(filename)
    title=f.readline(2048)
    while(title):
		#print title
		if "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title:			

			add_line_to_file(title,'ipissue.txt', insert)				
			title=f.readline(2048)
			continue
		if "blankblankblankblank".upper() in title.upper() or "FsmEndpProcEvntUm" in title or "EndpAddReg reg" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title:			

			add_line_to_file(title,'ipissue.txt', insert)				
			title=f.readline(2048)
			continue

			
		title=f.readline(2048)
    f.close()
 

    
       
        
analyse_file('main')
analyse_file('missinglog')
analyse_file('imsbr')
analyse_file('radio')
analyse_file('events')
analyse_file('system')
analyse_file('mtc')
 


