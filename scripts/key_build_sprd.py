# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:57:59 2016

@author: evers.chen
"""
import sys  
import glob  
import os  
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
        pos1 = 0
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

    
def outputKey(filename):
    f=open(filename)
    ff=f.read()
    f.close()
 
    SPI_i=""
    
    eik='parsed IKE_SA_INIT response'
    pos1 = ff.find(eik)
    while pos1 != -1:
        stepin='selected proposal:'
        pos11 = ff.find(stepin ,pos1)
        if pos11 == -1:
            pos1 = ff.find(eik ,pos1+1)
            continue
        pos1 = pos11
        match2='\n'
        pos3 = ff.find(match2,pos1)
        ret = ff[pos1 + 23:pos3]
        a=ret.split("/")
        print a
        enc_alg=a[0].replace('_','-')       
        enc_alg='"'+enc_alg+' [RFC3602]"'
        int_alg='"'+a[1]+' [RFC2404]"'
        match2="natd_chunk ="
        pos3 = ff.find(match2,pos1)
        if pos3 != -1:
            match2="[IKE]    0:"
            pos4 = ff.find(match2,pos3)
            ret = ff[pos4 + 12:pos4+59]  
            print ret
            SPI_i=ff[pos4 + 12:pos4+35]
            SPI_i=SPI_i.replace(' ','') 
            SPI_r=ff[pos4 + 36:pos4+59]
            SPI_r=SPI_r.replace(' ','')
            
            match2="Sk_ai secret ="
            pos3 = ff.find(match2,pos1)
            match2="[IKE]    0:"
            pos4 = ff.find(match2,pos3)
            ret = ff[pos4 + 12:pos4+59]
            SK_ai=ret
            match2="[IKE]   16:"
            pos4 = ff.find(match2,pos3)
            ret = ff[pos4 + 12:pos4+23]
            SK_ai=SK_ai+ret
            SK_ai=SK_ai.replace(' ','')
            
            match2="Sk_ar secret ="
            pos3 = ff.find(match2,pos1)
            match2="[IKE]    0:"
            pos4 = ff.find(match2,pos3)
            ret = ff[pos4 + 12:pos4+59]
            SK_ar=ret
            match2="[IKE]   16:"
            pos4 = ff.find(match2,pos3)
            ret = ff[pos4 + 12:pos4+23]
            SK_ar=SK_ar+ret
            SK_ar=SK_ar.replace(' ','')
    
    
            match2="Sk_ei secret ="
            pos3 = ff.find(match2,pos1)
            match2="[IKE]    0:"
            pos4 = ff.find(match2,pos3)
            ret = ff[pos4 + 12:pos4+59]
            SK_ei=ret
            SK_ei=SK_ei.replace(' ','')
    
            match2="Sk_er secret ="
            pos3 = ff.find(match2,pos1)
            match2="[IKE]    0:"
            pos4 = ff.find(match2,pos3)
            ret = ff[pos4 + 12:pos4+59]
            SK_er=ret
            SK_er=SK_er.replace(' ','')
    
    
             
            print "SPI_i:"+SPI_i
            print "SPI_r:"+SPI_r       
            print "SK_ei:"+SK_ei
            print "SK_er:"+SK_er
            print "enc_alg:"+enc_alg
            print "SK_ai:"+SK_ai
            print "SK_ar:"+SK_ar
            print "int_alg:"+int_alg
    
            add_line_to_ike(SPI_i+","+SPI_r+","+SK_ei+","+SK_er+","+enc_alg+","+SK_ai+","+SK_ar+","+int_alg)
            
        pos1 = ff.find(eik ,pos1)
        

    
    #----------------------------------------------------------------------

    
    pattern='SECURITY IKE_KEY:'
    pos1 = ff.find(pattern)
    while pos1 != -1:
        match2='\n'
        pos3 = ff.find(match2,pos1)
        ret = ff[pos1 + len(pattern):pos3]
        print ret
    	add_line_to_ike(ret)
    	pos1 = ff.find(pattern ,pos3)

    eik='SessResultDump Virtual Ip <'
    pos = ff.find(eik)    
    while pos != -1:        
        SPI_i=""
        eik='encryption initiator key ='
        pos1 = pos
    
        if SPI_i:
            #print "SPI_i:"+SPI_i
            print "SPI_i_sa:"+SPI_i_sa
    
            print "src_i:"+src_i
            print "dst_i:"+dst_i
            #print "SPI_r:"+SPI_r
            print "SPI_r_sa:"+SPI_r_sa
            print "src_r:"+src_r
            print "dst_r:"+dst_r        
            print "SK_ei:"+SK_ei
            print "SK_er:"+SK_er
            #print "enc_alg:"+enc_alg
            print "enc_alg_sa:"+enc_alg_sa
            print "SK_ai:"+SK_ai
            print "SK_ar:"+SK_ar
            #print "int_alg:"+int_alg
            print "int_alg_sa:"+int_alg_sa
            
            add_line_to_esp_sa(IP_type+","+src_i+","+dst_i+","+SPI_i_sa+","+enc_alg_sa+","+"\"0x"+SK_ei+"\""+","+int_alg_sa+","+"\"0x"+SK_ai+"\"")
            add_line_to_esp_sa(IP_type+","+src_r+","+dst_r+","+SPI_r_sa+","+enc_alg_sa+","+"\"0x"+SK_er+"\""+","+int_alg_sa+","+"\"0x"+SK_ar+"\"")
    
        pos = ff.find(eik,pos+1) 
	
	exit(0) 
    #----------------------------------------------------------------------
	
    
    eik='encryption initiator key ='
    pos = ff.find(eik)    
    while pos != -1:        
        SPI_i=""
        eik='encryption initiator key ='
        pos1 = pos
        if pos1 != -1:
            match='[CHD]    0: '
            pos2 = ff.find(match,pos1)
            ret = ff[pos2 + 12:pos2+12+47]
            SK_ei=ret.replace(' ','')
            print "encryption initiator key = "+"0x" + ret.replace(' ','')
        
     
        iik='integrity initiator key ='
        pos1 = ff.find(iik,pos)
        if pos1 != -1:
            match ='[CHD]    0: '
            pos2 = ff.find(match,pos1)
            ret1 = ff[pos2 + 12:pos2+12+47]
            match2='[CHD]   16: '
            pos2 = ff.find(match2,pos1)
            ret2 = ff[pos2 + 12:pos2+12+11]
            ret=ret1+ret2
            SK_ai=ret.replace(' ','')
            print "integrity initiator key  = "+"0x" + ret.replace(' ','')
            
    
        outbound='adding outbound ESP SA'        
        pos1 = ff.find(outbound,pos)
        if pos1 != -1:
            match ='[CHD]   SPI'
            pos2 = ff.find(match,pos1)
            
            match2='\n'
            pos3 = ff.find(match2,pos2)
            ret = ff[pos2 + 8:pos3]
            
            SPI_i=ret
            match2='0x'
            pos3 = SPI_i.find(match2,0)
            match3=','
            pos4 = SPI_i.find(match3,pos3)
            SPI_i=SPI_i[pos3+len(match2):pos4]
            SPI_i_sa='"0x'+SPI_i+'"'
            sStr1 = '0000000000000000'
            n = 16 - len(SPI_i)
            SPI_i =sStr1[0:n] + SPI_i
    
            src_i=ret
            match2='src'
            pos3 = src_i.find(match2,0)
            match3='dst'
            pos4 = src_i.find(match3,pos3)
            src_i=src_i[pos3+len(match2):pos4]
            src_i=src_i.replace(' ','')
            src_i='"'+src_i+'"'
    
            dst_i=ret
            match2='dst'
            pos3 = dst_i.find(match2,0)
            match3='\n'
            pos4 = dst_i.find(match3,pos3)
            dst_i=dst_i[pos3+len(match2):]
            dst_i=dst_i.replace('\n','')
            dst_i=dst_i.replace('\r','')
            dst_i=dst_i.replace(' ','')
            dst_i='"'+dst_i+'"'
            IP_type='"IPv4"'
            print "outbound ESP SA = " + ret
            
            match3='using encryption algorithm'
            pos3 = ff.find(match3,pos1)
            match2='\n'
            pos4 = ff.find(match2,pos3)
            enc_alg=ff[pos3:pos4]
            size=enc_alg
            print ff[pos3:pos4]
            
            match2='algorithm'
            pos3 = enc_alg.find(match2,0)
            match3='with'
            pos4 = enc_alg.find(match3,pos3)
            enc_alg=enc_alg[pos3+len(match2):pos4]
                 
     
            match2='size'
            pos3 = size.find(match2,0)
            match3='\r'
            pos4 = size.find(match3,pos3)
            size=size[pos3+len(match2)+1:]
            size=size.replace('\n','')
            size=size.replace('\r','')
            
            enc_alg_sa=enc_alg.replace(' ','')
            enc_alg_sa=enc_alg_sa.replace('_','-')       
            enc_alg_sa='"'+enc_alg_sa+' [RFC3602]"'
            
            enc_alg=enc_alg.replace(' ','')+'_'+size        
            enc_alg=enc_alg.replace('_','-')       
            enc_alg='"'+enc_alg+' [RFC3602]"'
                   
            
    
            match3='using integrity algorithm'
            pos3 = ff.find(match3,pos1)
            match2='\n'
            pos4 = ff.find(match2,pos3)
            int_alg=ff[pos3:pos4]
            print ff[pos3:pos4]
            
            match2='algorithm'
            pos3 = int_alg.find(match2,0)
            match3='with'
            pos4 = int_alg.find(match3,pos3)
            int_alg=int_alg[pos3+len(match2):pos4]
            int_alg='"'+int_alg.replace(" ","")+' [RFC2404]"'
            if int_alg=='"HMAC_SHA1_96 [RFC2404]"':
                int_alg_sa='"HMAC-SHA-1-96 [RFC2404]"'    
            else:
                int_alg_sa=int_alg
            print
    
      
        irk='integrity responder key ='
        pos1 = ff.find(irk,pos)
        if pos1 != -1:
            match ='[CHD]    0: '
            pos2 = ff.find(match,pos1)
            ret1 = ff[pos2 + 12:pos2+12+47]
            match2='[CHD]   16: '
            pos2 = ff.find(match2,pos1)
            ret2 = ff[pos2 + 12:pos2+12+11]
            ret=ret1+ret2
            SK_ar=ret.replace(' ','')
            print "integrity responder key  = "+"0x" + ret.replace(' ','')
    
            
        erk='encryption responder key ='
        pos1 = ff.find(erk,pos)
        if pos1 != -1:
            match='[CHD]    0: '
            pos2 = ff.find(match,pos1)
            ret = ff[pos2 + 12:pos2+12+47]
            SK_er=ret.replace(' ','')
            print "encryption responder key = "+"0x" + ret.replace(' ','')
    
        inbound='adding inbound ESP SA'        
        pos1 = ff.find(inbound,pos)
        if pos1 != -1:
            IP_type='"IPv4"'
            match ='[CHD]   SPI'
            pos2 = ff.find(match,pos1)
            
            match2='\n'
            pos3 = ff.find(match2,pos2)
            ret = ff[pos2 + 8:pos3]
            SPI_r=ret
    
            src_r=ret
            match2='src'
            pos3 = src_r.find(match2,0)
            match3='dst'
            pos4 = src_r.find(match3,pos3)
            src_r=src_r[pos3+len(match2):pos4]
            src_r=src_r.replace(' ','')
            src_r='"'+src_r+'"'
    
            dst_r=ret
            match2='dst'
            pos3 = dst_r.find(match2,0)
            match3='\n'
            pos4 = dst_r.find(match3,pos3)
            dst_r=dst_r[pos3+len(match2):]
            dst_r=dst_r.replace('\n','')
            dst_r=dst_r.replace('\r','')
            dst_r=dst_r.replace(' ','')
            dst_r='"'+dst_r+'"'
            
            match2='0x'
            pos3 = SPI_r.find(match2,0)
            match3=','
            pos4 = SPI_r.find(match3,pos3)
            SPI_r=SPI_r[pos3+len(match2):pos4]
            SPI_r_sa='"0x'+SPI_r+'"'
            sStr1 = '0000000000000000'
            n = 16 - len(SPI_r)
            SPI_r =sStr1[0:n] + SPI_r        
            print "inbound ESP SA = " + ret
            
            match3='using encryption algorithm'
            pos3 = ff.find(match3,pos1)
            match2='\n'
            pos4 = ff.find(match2,pos3)
            print ff[pos3:pos4]
    
            match3='using integrity algorithm'
            pos3 = ff.find(match3,pos1)
            match2='\n'
            pos4 = ff.find(match2,pos3)
            print ff[pos3:pos4]
            print 
    
    
        if SPI_i:
            #print "SPI_i:"+SPI_i
            print "SPI_i_sa:"+SPI_i_sa
    
            print "src_i:"+src_i
            print "dst_i:"+dst_i
            #print "SPI_r:"+SPI_r
            print "SPI_r_sa:"+SPI_r_sa
            print "src_r:"+src_r
            print "dst_r:"+dst_r        
            print "SK_ei:"+SK_ei
            print "SK_er:"+SK_er
            #print "enc_alg:"+enc_alg
            print "enc_alg_sa:"+enc_alg_sa
            print "SK_ai:"+SK_ai
            print "SK_ar:"+SK_ar
            #print "int_alg:"+int_alg
            print "int_alg_sa:"+int_alg_sa
            
            add_line_to_esp_sa(IP_type+","+src_i+","+dst_i+","+SPI_i_sa+","+enc_alg_sa+","+"\"0x"+SK_ei+"\""+","+int_alg_sa+","+"\"0x"+SK_ai+"\"")
            add_line_to_esp_sa(IP_type+","+src_r+","+dst_r+","+SPI_r_sa+","+enc_alg_sa+","+"\"0x"+SK_er+"\""+","+int_alg_sa+","+"\"0x"+SK_ar+"\"")
    
        pos = ff.find(eik,pos+1) 


#----------------------------------------------------------------------

                
    aalg=["NULL","HMAC-MD5-96 [RFC2403]","HMAC-SHA-1-96 [RFC2404]","HMAC-SHA-256-128 [RFC4868]","HMAC-SHA-384-192 [RFC4868]","HMAC-SHA-512-256 [RFC4868]","MAC-RIPEMD-160-96 [RFC2857]"]
    ealg=["NULL","DES-CBC [RFC2405]","TripleDES-CBC [RFC2451]","CAST5-CBC [RFC2144]","BLOWFISH-CBC [RFC2451]","AES-CBC [RFC3602]"]

    IP_type='"IPv4"'	
    iptypecheck='RegSetupSa'
    pos1 = ff.find(iptypecheck)
    if pos1 == -1:
		print "no RegSetupSa, exit here"
#		time.sleep( 5000 )
#		sys.exit(0)		
    if pos1 != -1:
		iptypecheck='iAfC:'
		pos1 = ff.find(iptypecheck,pos1)
		match =','
		pos2 = ff.find(match,pos1)
		ret = ff[pos1 + 5:pos2]
		if ret=='1':
			IP_type='"IPv6"'

    print "IP address: "+ IP_type
	
    ipsec='"ZIpsecPfkeyParmSpi":'   
    i=0
    pos1 = ff.find(ipsec)
    while pos1 != -1:
 
        spi_sa=[0,0,0,0]
        auth_type_sa=["","","",""]
        auth_key_sa=["","","",""]
        enc_key_sa=["","","",""]
        enc_type_sa=["","","",""]
        src_add_sa=["","","",""]
        dst_add_sa=["","","",""]
     
        match =','
        pos2 = ff.find(match,pos1)
        ret = ff[pos1 + 21:pos2]
    	if int(ret) == 0: 
    		pos1 = ff.find(ipsec,pos1 +1)
    		continue
        print "SIP SPI : " + ret+" = "+hex(int(ret))
        spi_sa[i]=str(hex(int(ret)))
        spi_sa[i]=spi_sa[i][2:]
        print "spi_sa[0]=",spi_sa[i]
        if spi_sa[i][-1]=='L':
            spi_sa[i]=spi_sa[i][0:len(spi_sa[i])-1]
            print "spi_sa[0]=",spi_sa[i]
        sStr1 = '00000000'
        n = 8 - len(spi_sa[i])
        if n:
            spi_sa[i] =sStr1[0:n] + spi_sa[i]
        spi_sa[i]='0x'+spi_sa[i]
        print "inbound ESP SA = " + ret
          
        match2='ZIpsecPfkeyParmAuthKey'
        pos3 = ff.find(match2,pos2)
        match3='",'
        pos4 = ff.find(match3,pos3)
        if pos3 ==-1 or pos4==-1 :
            pos1 = ff.find(ipsec,pos1 +1)
            continue
        print "AuthKey:val 0x"+ff[pos3+len(match2)+3:pos4]
        auth_key_sa[i] = "0x"+ ff[pos3+len(match2)+3:pos4]

        match2='ZIpsecPfkeyParmAuthType'
        pos3 = ff.find(match2,pos2)
        match3=','
        pos4 = ff.find(match3,pos3)
        if pos3 ==-1 or pos4==-1 :
            pos1 = ff.find(ipsec,pos1 +1)
            continue
        print "AuthType: "+ff[pos3+len(match2)+2:pos4]
        auth_type_sa[i]=int(ff[pos3+len(match2)+2:pos4])
        
        
        match2='ZIpsecPfkeyParmEncKey'
        pos3 = ff.find(match2,pos2)
        match3='",'
        pos4 = ff.find(match3,pos3)
        if pos3 ==-1 or pos4==-1 :
            pos1 = ff.find(ipsec,pos1 +1)
            continue
        print "EncKey:  0x"+ff[pos3+len(match2)+3:pos4]
        enc_key_sa[i]="0x"+ ff[pos3+len(match2)+3:pos4]

        match2='ZIpsecPfkeyParmEncType'
        pos3 = ff.find(match2,pos2)
        match3=','
        pos4 = ff.find(match3,pos3)
        if pos3 ==-1 or pos4==-1 :
            pos1 = ff.find(ipsec,pos1 +1)
            continue
        print "EncType: "+ff[pos3+len(match2)+2:pos4]
        enc_type_sa[i]=int(ff[pos3+len(match2)+2:pos4])


 
        match2='ZIpsecPfkeyParmSrcAddr'
        pos3 = ff.find(match2,pos2)
        match3='",'
        pos4 = ff.find(match3,pos3)
        if pos3 ==-1 or pos4==-1 :
            pos1 = ff.find(ipsec,pos1 +1)
            continue
        print "SrcAddr:  "+ff[pos3+len(match2)+3:pos4]
        src_add_sa[i]=ff[pos3+len(match2)+3:pos4]

        match2='ZIpsecPfkeyParmSrcPort'
        pos3 = ff.find(match2,pos2)
        match3='",'
        pos4 = ff.find(match3,pos3)
        if pos3 ==-1 or pos4==-1 :
            pos1 = ff.find(ipsec,pos1 +1)
            continue
        print "SrcPort:  "+ff[pos3+len(match2)+3:pos4]
        

        match2='ZIpsecPfkeyParmDstAddr'
        pos3 = ff.find(match2,pos2)
        match3='",'
        pos4 = ff.find(match3,pos3)
        if pos3 ==-1 or pos4==-1 :
            pos1 = ff.find(ipsec,pos1 +1)
            continue
        print "DstAddr:  "+ff[pos3+len(match2)+3:pos4]
        dst_add_sa[i]=ff[pos3+len(match2)+3:pos4]
        
        match2='ZIpsecPfkeyParmDstPort'
        pos3 = ff.find(match2,pos2)
        match3='",'
        pos4 = ff.find(match3,pos3)
        if pos3 ==-1 or pos4==-1 :
            pos1 = ff.find(ipsec,pos1 +1)
            continue
        print "DstPort:  "+ff[pos3+len(match2)+3:pos4]
        print
        pos1 = ff.find(ipsec,pos1 +1)
        
        add_line_to_esp_sa(IP_type+","+"\""+src_add_sa[0]+"\""+","+"\""+dst_add_sa[0]+"\""+","+"\""+spi_sa[0]+"\""+","+"\""+ealg[enc_type_sa[0]]+"\""+","+"\""+enc_key_sa[0]+"\""+","+"\""+aalg[auth_type_sa[0]]+"\""+","+"\""+auth_key_sa[0]+"\"")
        
              

       
    print
    
       
        

dir = 'E:\\LOG\\20160318-135756'  
dir = './'  
suffix = 'log'  
f = glob.glob(dir + '\\*.' + suffix)  
print f 
for file in f :  
    filename = os.path.basename(file)  
    print file
    outputKey(file)        
    print

