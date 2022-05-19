# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:57:59 2016

@author: evers.chen
"""
import sys  
import glob  
import os  
import _winreg
     
#coding=gbk    
import shutil, string
import time  
mp3List = "F:\\My Documents\\mp3list\\默认精选.m3u"  

def add_line_to_file(title, filename, insert):
    str_len=18
    insert=0
    #print filename	
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
			
def cpFile(srcPath, destDir, pathdes):  
	fileName = os.path.basename(srcPath)
	if not os.path.exists(destDir):
		os.makedirs(destDir) 
	destPath = destDir + os.path.sep + fileName
	#print 'src=',srcPath
	#print 'dest=',destPath

	if os.path.exists(srcPath) and not os.path.exists(destPath):  
		#print 'cp %s %s' % (srcPath,destPath)  
		shutil.copy(srcPath,destPath)
	else:
		print 'failed to copy:',srcPath
		add_line_to_file(srcPath+'\n',pathdes+'\\failed-to-copy.txt',0)

		
def analyse_file(file_name_filter):
	dir = './'  
	suffix = 'txt'  
	f = glob.glob(dir + '\\'+file_name_filter+'*.' + suffix)  
	for file in f :  
		filename = os.path.basename(file)  
		#print file
		path='E:\\source-code\\'
		path=path+time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
		outputKey(file, path)        

    
def outputKey(filename, pathdes):
	num=1	
	f=open(filename)
	title=f.readline(2048)
	#print pathdes
	while(title):
		#print num,title
		pathName = os.path.dirname(title.strip())
		#print pathName
		destpath=pathName[2:]
		destpath=pathdes+destpath
		#print destpath
		#add_line_to_file(title,'system_behavior.txt', insert)
		print 'copy:',num
		cpFile(title.strip(), destpath, pathdes)
		title=f.readline(2048)
		
		num=num+1
		#if num==3:
		#	break

	f.close()
 
  
analyse_file('file-list')

 


