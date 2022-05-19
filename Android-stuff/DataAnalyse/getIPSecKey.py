#!/usr/bin/python
# -*- coding: utf-8 -*-
#mingzhe.jin 
#2017.05.01


import re
import os 
import glob
import _winreg
import time
import Tkinter

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
	#keywords
	K_add_src = 'add src'	
	Kspace = ' '
	K0x = '0x'
	
	K_mode_auth = 'mode'
	K_enc = 'enc'
	
	K_spi = 'spi'
	K_src = 'src'
	K_dst = 'dst'
	
	K_auth_ha1 = 'ha1'
	K_auth_md5 = 'md5'
	K_auth_sha256_128 = 'sha256-128'
	K_auth_sha384 = 'sha384'
	K_auth_sha512 = 'sha512'
	#K_auth_rmd160 = 'rmd160'
	K_auth_unknow = 'unkown'
	
	K_enc_des3 = 'des3_ede'
	K_enc_aes = 'aes'
	K_enc_des = 'des'
	K_enc_cast5 = 'cast5'
	K_enc_blowfish = 'blowfish'
	K_cipher_null = 'cipher_null'
	
	IP_type4='"IPv4"'
	IP_type6='"IPv6"'
	
	#Authentication
	auth_null = '"NULL"'
	hmac_sha1 = '"HMAC-SHA-1-96 [RFC2404]"'
	hmac_md5 = '"HMAC-MD5-96 [RFC2403]"'
	hmac_sha_256_96 = 'HMAC-SHA-256-96 [draft-ietf-ipsec-ciph-sha-256-00]' 
	hmac_sha_256_128 = 'HMAC-SHA-256-128 [RFC4868]'
	hmac_sha_384_192 = 'HMAC-SHA-384-192 [RFC4868]'
	hmac_sha_512_256 = 'HMAC-SHA-512-256 [RFC4868]'
	hmac_md5_96 = 'HMAC-MD5-96 [RFC2043]'
	
	#Ecryption
	enc_cipher_null = '"NULL"'
	aes_cbc = '"AES-CBC [RFC3602]"'
	aes_ctr = '"AES-CTR [RFC3686]"'
	des_cbc3 = '"TripleDES-CBC [RFC2451]"'
	des_cbc = '"DES_CBC [RFC2045]"'
	cast5_cbc = '"CAST5-CBC [RFC2144]"'
	blowfish_cbc = '"BLOWFISH-CBC [RFC2451]"'
	twofish_cbc = '"TWOFISH-CBC"'
	aes_gcm = '"AES-GCM [rfc4106]"'

	#start
	bufferlines = []
	fileObject = open(fileName, "r+")
	fileReadlines = fileObject.readlines()
	fileObject.close()

	lineFilter = 'ip xfrm state add'
	for line in fileReadlines:
		if lineFilter in line:
			bufferlines.append(line)


	for lines in bufferlines:
		lines = lines.strip()  #default to delete '/t','/r','/n'
		#linestring = ''.join(lines)
		#kAddrSrcFindResult = lines.find(K_add_src)
		#while keyWordsFindResult !=-1:
		#print keyWordsFindResult
		#src IP
		srcIPs = lines.find(K_src)
		
		#dst IP
		dstIPs = lines.find(K_dst)
		#print  "dstIPs = ",dstIPs
		
		#judge it is IPV4 or IPV6
		if (lines.find(":",srcIPs,dstIPs) != -1):
			IP_Type = IP_type6
		else:
			IP_Type = IP_type4
		
		print "IP_Type = ",IP_Type
		
		#end of src IP 
		KSpaceFindResult = lines.find(Kspace, srcIPs+4)
		#search srcIP value
		srcIP = lines[srcIPs+4 : KSpaceFindResult]
		print "srcIP = ",srcIP
		
		#end of dst IP 
		KSpaceFindResult = lines.find(Kspace, dstIPs+4)
		#search desIP value
		dstIP = lines[dstIPs+4 : KSpaceFindResult]
		print "dstIP = ",dstIP
		
		#spi
		spi = lines.find(K_spi)
		#end of spi
		KSpaceFindResult = lines.find(Kspace, spi+4)
		#search spi value
		spi = lines[spi+4 : KSpaceFindResult]
		print "spi = ", spi
        
		#Auth_Type
		if (lines.find(K_auth_ha1) != -1):
			Auth_Type = hmac_sha1
			print "Auth_Type = ",Auth_Type 
		elif (lines.find(K_auth_md5) != -1):
			Auth_Type = hmac_md5
			print "Auth_Type = ",Auth_Type 
		elif (lines.find(K_auth_unknow) != -1):
			Auth_Type = auth_null
			print "Auth_Type = ",Auth_Type
		elif (lines.find(K_auth_sha256_128) != -1):
			Auth_Type = hmac_sha_256_128
			print "Auth_Type = ",Auth_Type
		elif (lines.find(K_auth_sha384) != -1):
			Auth_Type = hmac_sha_384_192
			print "Auth_Type = ",Auth_Type	
		elif (lines.find(K_auth_sha512) != -1):
			Auth_Type = hmac_sha_512_256
			print "Auth_Type = ",Auth_Type
		else:
			print "[Error:] uncomparable Auth_Type"
			
		#mode tansport location
		modeAuth = lines.find(K_mode_auth)
			
		#Auth value
		#if auth is NULL, the auth value is null
		if (Auth_Type is auth_null):
			auth = ""
			print "[INFO:] auth value is none"
		else:
		    #start of auth value 
			KValueFindResult = lines.find(K0x, modeAuth)
			#end of auth value 
			KSpaceFindResult = lines.find(Kspace, KValueFindResult)
			#auth value 
			auth = lines[KValueFindResult : KSpaceFindResult]
		
		print "auth = ",auth
		
		
		#Enc_Type
		if (lines.find(K_enc_aes) != -1):
			ENC_Type = aes_cbc
			print "Enc_Type = ",ENC_Type 
		elif (lines.find(K_enc_des3) != -1):
			ENC_Type = des_cbc3
			print "Enc_Type = ",ENC_Type 
		elif (lines.find(K_cipher_null) != -1):
			ENC_Type = enc_cipher_null
			print "Enc_Type = ",ENC_Type
		elif (lines.find(K_enc_des) != -1):
			ENC_Type = des_cbc
			print "Enc_Type = ",ENC_Type
		else:
			print "[Error:] uncomparable ENC_Type"
			
		#mode tansport location
		encFind = lines.find(K_enc)
			
		#Enc value
		#if auth is NULL, the auth value is null
		if (ENC_Type is enc_cipher_null):
			enc = ""
			print "[INFO:] enc value is none"
		else:
		    #start of enc value 
			KValueFindResult = lines.find(K0x, encFind)
			#end of enc value 
			KSpaceFindResult = lines.find(Kspace, KValueFindResult)
			#enc value 
			enc = lines[KValueFindResult : KSpaceFindResult]
		
		print "enc = ",enc
			
		#print "ok"
		add_line_to_esp_sa(IP_Type+","+"\""+srcIP+"\""+","+"\""+dstIP+"\""+","+"\""+spi+"\""+","+ENC_Type+","+"\""+enc+"\""+","+Auth_Type+","+"\""+auth+"\"")

	print

def outputKey(fileName):
	ike_sa_key(fileName)
	ipsec_sa_key(fileName)
	
dir = './'  
suffix = 'ylog'
suffixs = 'log'  
f1 = glob.glob(dir + '\\*.' + suffix) 
f2 = glob.glob(dir + '\\*.' + suffixs)
print f1
print f2 

for file in f2 :  
    filename = os.path.basename(file)  
    print file
    outputKey(file)        
    print
	
for file in f1 :  
    filename = os.path.basename(file)  
    print file
    outputKey(file)        
    print
	