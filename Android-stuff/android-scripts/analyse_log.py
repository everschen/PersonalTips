# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:57:59 2016

@author: evers.chen
"""
import sys  
import glob  
import os  
import _winreg
     
def add_line_to_file(ike_str,filename):
    cfg_ike="radio.txt"
    file_object = open(filename, 'a+')
#    file_object.read()
    file_object.write(ike_str)
    file_object.close( )




def add_line_to_esp_sa(sa_str):
    
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Wireshark")
    value, type = _winreg.QueryValueEx(key, "VersionMinor")
    print "Your wireshark version 1." + str(value)

    cfg_sa=os.getenv('APPDATA')+"\Wireshark\esp_sa"
    print "Your wireshark esp sa file: " + cfg_sa

    if (len(sa_str)>20480) :
        print sa_str
        return
        
    with open(cfg_sa) as f:
        fff=open(cfg_sa)
        ff=fff.read()
        pos1 = ff.find(sa_str)
        
        if pos1 != -1:
            print sa_str+" already existed!"
        else:
            lines = f.readlines()
            lines[1:1] = [sa_str+'\n']
            open(cfg_sa, 'w').writelines(lines)
            print "Insert key "+sa_str + " successfually!"
        print
        print
            
  

    
def outputKey(filename):
    f=open(filename)
    title=f.readline(2048)
    while(title):
		if "^CONN" in title or "+CIREGU" in title or "+CIREG?" in title or "+IMSHO" in title or "+VOWFREG" in title or "+IMSWFATT" in title or "+IMSHOWFINF" in title or "+IMSHOCALLEND" in title or "+VOWIFIEN" in title:
			print title
			add_line_to_file(title,'result.txt')
		if "ImsCMUtils" in title:
			print title
			add_line_to_file(title,'result.txt')
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
    add_line_to_file('\n','result.txt')

