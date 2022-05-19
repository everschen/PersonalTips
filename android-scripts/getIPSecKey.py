# -*- coding: utf-8 -*-
#mingzhe.jin 
#2016.09.28

import re
import os 
import glob
import _winreg
import time

def add_line_to_ike(ike_str):
    
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Wireshark")
    value, type = _winreg.QueryValueEx(key, "VersionMinor")
    print "Your wireshark version 1." + str(value)

    cfg_ike=os.getenv('APPDATA')+"\Wireshark\ikev2_decryption_table"
    print "Your wireshark ikev2 file: " + cfg_ike

    with open(cfg_ike) as f:
        fff=open(cfg_ike)
        ff=fff.read()
        pos1 = ff.find(ike_str)
        #pos1 = 1
        
        if pos1 != -1:
            print ike_str+" already existed!"
        else:
            lines = f.readlines()
            lines[1:1] = [ike_str+'\n']
            open(cfg_ike, 'w').writelines(lines)
            print "Insert key "+ike_str + " successfually!"
        print
        print
        

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

def ike_sa_key(fileName):		
	f = open(fileName, "r+")
	ff=f.read()
	f.close()
	eik='IKE_KEY:'
	pos1 = ff.find(eik)

	while pos1 != -1:
			ike_str = ff[pos1+8:pos1+238]
			print ike_str
			add_line_to_ike(ike_str)
			pos1 = ff.find(eik,pos1+1)

def ipsec_sa_key(fileName):
	#keyWords = 'ip xfrm state add'
	keyWords = 'add src'
	src = 'add src'
	dst = 'dst'
	proto = 'proto esp spi'
	mode = 'mode'
	ha1 = 'ha1'
	md5 = 'md5'
	enc_des3 = 'enc des3_ede'
	enc_aes = 'enc aes'
	enc_aes_end = 'reqid'
	IP_type4='"IPv4"'
	IP_type6='"IPv6"'
	aes_cbc = '"AES-CBC [RFC3602]"'
	des_cbc3 = '"TripleDES-CBC [RFC2451]"'
	hmac_sha1 = '"HMAC-SHA-1-96 [RFC2404]"'
	hmac_md5 = '"HMAC-MD5-96 [RFC2403]"'
	
	fff=open(fileName)
	ff=fff.read()
	pos1 = ff.find('S2bSwitchLogin:Ipv6')
	IP_Type = IP_type4
	if pos1 !=-1:
		IP_Type = IP_type6
		
	fileObject = open(fileName, "r+")
	fileReadlines = fileObject.readlines()
		
	fileObject.close()
	fileWrite = open('E:\\LOG\\tmp.txt', "w+")

	#lineFilter = 'JuIpsecServer: Server Recv'
	lineFilter = 'ip xfrm state add'
	for line in fileReadlines:
		if lineFilter in line:
			fileWrite.write(line)	
	fileWrite.close()

	fileReader = open('E:\\LOG\\tmp.txt', "r+")
	fileRead = fileReader.readlines()

	#fileRead.strip(' ');
	#fileRead.strip('\t');
	#print fileRead 
	#print fileRead
	#fileRead.close()

	for lines in fileRead:
		lines = lines.strip()
		#linestring = ''.join(lines)
		keyWordsFindResult = lines.find(keyWords)
		#while keyWordsFindResult !=-1:
		#print keyWordsFindResult
		#src IP
		srcIPs = lines.find(src)
		
		#keyWordsFindResult = srcIPs
		dstIPs = lines.find(dst)
		#print  "dstIPs = ",dstIPs
		
		srcIP = lines[srcIPs+8 : dstIPs-1]
		print "srcIP = ",srcIP
		
		#dst IP 
		#keyWordsFindResult = dstIPs
		protos = lines.find(proto)
		#print  "protos = ",protos
		
		dstIP = lines[dstIPs+4 : protos-1]
		print "dstIP = ",dstIP
		
		#spi
		#keyWordsFindResult = protos
		modess = lines.find(mode)
		spi = lines[protos+14 : protos+24]
		print "spi = ", spi
        
        #keyWordsFindResult = modess
		modes = lines.find(ha1)
		if modes == -1:
			modes = lines.find(md5)
			isSha1 = False
		else:
			isSha1 = True
		print "isSha1 = ",isSha1
		spi = lines[protos+14 : modess-1]
		
		#auth
		#keyWordsFindResult = modes
		
		enc_aess = lines.find(enc_des3)
		if enc_aess != -1:
			ENC_Type = des_cbc3
			print ENC_Type
		else:
			enc_aess = lines.find(enc_aes)
			ENC_Type = aes_cbc
			print ENC_Type

		auth = lines[modes+4 : enc_aess-1]
		print "auth = ",auth
		
		#enc
		#keyWordsFindResult = enc_aess
		enc_aesbegin = lines.find('0x',enc_aess)
		enc_aesend = lines.find(enc_aes_end)
		enc = lines[enc_aesbegin : enc_aesend-1]
		print "enc = ",enc
		
		#IP type & Auth
		if isSha1 == True:
			
			Auth_Type = hmac_sha1
		else:
			
			Auth_Type = hmac_md5
			
		#AES-CBC
		#ENC_Type = aes_cbc
		#print "ok"
		add_line_to_esp_sa(IP_Type+","+"\""+srcIP+"\""+","+"\""+dstIP+"\""+","+"\""+spi+"\""+","+ENC_Type+","+"\""+enc+"\""+","+Auth_Type+","+"\""+auth+"\"")
		#keyWordsFindResult = enc_aesend
		#print "enc_aesend",enc_aesend
		#keyWordsFindResult = fileRead.find(keyWords,keyWordsFindResult)
	print

def outputKey(fileName):
	ike_sa_key(fileName)
	ipsec_sa_key(fileName)
	
dir = './'  
suffix = 'log'  
f = glob.glob(dir + '\\*.' + suffix) 
print f 
for file in f :   
    print file
    outputKey(file)        
    print
