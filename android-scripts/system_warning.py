# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:57:59 2016

@author: evers.chen
"""
import sys  
import glob  
import os  
import datetime


cur_is_mtc_file=0
	
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

			
			
def add_line_to_file(title, filename, insert, cur_is_mtc_file):
    str_len=18
    last_date=''	
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
			

    	if cur_is_mtc_file == 1 :
    		for i in range(0, len(lines)):
    			#print "i="+str(i)
    			#print "p1:"+lines[i]
    			#print "p2:"+lines[i][0:str_len]
    			#print "p3:"+title[0:str_len]
    			tmp = lines[i][0:6] + title
    			last_date = lines[i][0:6]	
    			if cmp(lines[i][0:str_len],tmp[0:str_len]) > 0 :
    				#print lines[i]
    				#print tmp
    				#print i
    				#print "---------------------"
    				lines[i:1] = [tmp]
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
    			#print title
    			lines[i:1] = [title]
    			open(filename, 'w').writelines(lines)
    			return
    		else:
    			#print "pos1"
    			continue

		
    	#print len(lines),i
    	if len(lines)-1 == i :
    		#print title
    		file_object = open(filename, 'a+')
    		file_object.write(last_date+title)
    		file_object.close()
    		return				
				
		#open(cfg_sa, 'w').writelines(lines)
           
  
def checknullvalue(cur_is_mtc_file, source, pattern):
	if pattern in source:
		ret=behindstr(source, pattern)
		if ret == "" :
			#print 'WARNING: '+ pattern + ret
			add_line_to_file(source,'system_warning.txt', 0, cur_is_mtc_file)
			add_line_to_file(source,'system_behavior.txt', 1, cur_is_mtc_file)
		else:
			print pattern+ret

def checkhasstring(cur_is_mtc_file, source, pattern):
	if pattern in source:
		#print 'WARNING: '+ pattern
		add_line_to_file(source,'system_warning.txt', 0, cur_is_mtc_file)
		add_line_to_file(source,'system_behavior.txt', 1, cur_is_mtc_file)

def checklogmissing(source, pattern):
	if pattern in source:
		#print 'WARNING: '+ pattern
		add_line_to_file(source,'system_logmissing.txt', 0, 0)
#		add_line_to_file(source,'system_behavior.txt', 1, cur_is_mtc_file)		

def checkhasserrortring(cur_is_mtc_file, source, pattern):
	if pattern in source:
		#print 'WARNING: '+ pattern
		add_line_to_file(source,'system_ERROR.txt', 888, cur_is_mtc_file)
		add_line_to_file(source,'system_behavior.txt', 1, cur_is_mtc_file)

def checksamevalue(cur_is_mtc_file, source, pattern):
	global last
	if pattern in source:

		ret=behindstr(source, pattern)
		if ret == "" :
			#print 'WARNING: '+ pattern + ret
			add_line_to_file(source,'system_warning.txt', 0, cur_is_mtc_file)
			add_line_to_file(source,'system_behavior.txt', 1, cur_is_mtc_file)
		else:
			print pattern+ret

			current = item()
			current.source = source
			current.value = ret
			currenttime = source[0:14]
			d1 = datetime.datetime.strptime(currenttime, '%m-%d %H:%M:%S')
			current.time = d1
			delta = current.time - last.time
			print "delta=",delta
			if (delta.seconds > 15):
				print "i am here "
				last = current
			else:
				print "i am there"
				if (last.value.lower() != current.value.lower()):
					print "ERROR: different ip address"
					currenttime = '01-01 12:09:31'
					d1 = datetime.datetime.strptime(currenttime, '%m-%d %H:%M:%S')
					last.time = d1	
					add_line_to_file(last.source,'system_ERROR.txt', 0, cur_is_mtc_file)
					add_line_to_file(current.source,'system_ERROR.txt', 0, cur_is_mtc_file)
				


			
def outputKey(filename):
    if "mtc" in filename:
    	cur_is_mtc_file=1
    else:
    	cur_is_mtc_file=0
		
    f=open(filename)
    title=f.readline(2048)
    while(title):
		
		checknullvalue(cur_is_mtc_file,title, 'volteip=')
		checknullvalue(cur_is_mtc_file,title, 'IMSREGADDR:')
		checknullvalue(cur_is_mtc_file,title, 'IMSHOCALLEND')
				
		checkhasstring(cur_is_mtc_file,title, 'ZOS: INFO: SocketLastErr:Invalid argument')
		checkhasstring(cur_is_mtc_file,title, 'ZOS: ERROR: sendto error')
		checkhasstring(cur_is_mtc_file,title, 'ZOS: ERROR: SendCmdToServer recvfrom')
		checkhasstring(cur_is_mtc_file,title, 'SECURITY IKE: INFO: Ike ResendTimer MsgId')
		checkhasstring(cur_is_mtc_file,title, 'Mrf_RegDelete')
		checkhasstring(cur_is_mtc_file,title, 'AT+CCMMD')
			
		checkhasserrortring(cur_is_mtc_file,title, 'MTC: ERROR: imei format is not correct!')
		checkhasserrortring(cur_is_mtc_file,title, 'SECURITY IKE: INFO:  Notify Message Type: INTERNAL_ADDRESS_FAILURE')
		checkhasserrortring(cur_is_mtc_file,title, 'failed reason = Repetitive operation')
		checkhasserrortring(cur_is_mtc_file,title, 'return only one ipsec sa pstOnlyOneSA')
		checkhasserrortring(cur_is_mtc_file,title, '[popup Vowifi unavailable notification]')
		checkhasserrortring(cur_is_mtc_file,title, 'AUTHENTICATION_FAILED')
		checkhasserrortring(cur_is_mtc_file,title, 'hung up Vowifi call')
		checkhasserrortring(cur_is_mtc_file,title, 'SECURITY IKE: INFO: SessAuthOnResendTmr Dpd Resend Timeout')
		checkhasserrortring(cur_is_mtc_file,title, 'can not re-register with empty info which used to handover')
		
		checkhasserrortring(cur_is_mtc_file,title, '[Adapter]Utilities: Can not get the ip address')
		checkhasserrortring(cur_is_mtc_file,title, 'SessAuthOnResendTmr Send Event')
		checkhasserrortring(cur_is_mtc_file,title, 'SessAuthOnResendTmr Dpd Resend Timeout')
		checkhasserrortring(cur_is_mtc_file,title, 'SessAuthOnResendTmr Resend Out')
		checkhasserrortring(cur_is_mtc_file,title, 'failed reason = Already handle one request')
		checkhasserrortring(cur_is_mtc_file,title, "Can't switch calls")
		checkhasserrortring(cur_is_mtc_file,title, 'EndpGetActReg Reg is not exist.')
		checkhasserrortring(cur_is_mtc_file,title, 'ERROR: S2bDeleteIpsec Failed')
		checkhasserrortring(cur_is_mtc_file,title, 'E [VoWifiService]RegisterService: Ping the pcscfIP')
		checkhasserrortring(cur_is_mtc_file,title, 'ImsConnectionManagerService: operationFailed')
		checkhasserrortring(cur_is_mtc_file,title, 'free twice')
		checkhasserrortring(cur_is_mtc_file,title, 'Cellular network is not available')
		checkhasserrortring(cur_is_mtc_file,title, 'NO PACKETS FROM CP, NEED CP CHECK IT FIRST')
		checkhasserrortring(cur_is_mtc_file,title, 'NO PACKETS RECV FROM WIFI, MAYBE IP CHANGED, SECURITY CHECK IT FIRST')
		checkhasserrortring(cur_is_mtc_file,title, 'NO VOWIFI TUPLES ADDED, BUT HANDOVER FROM VOWIFI TO VOLTE')
		checkhasserrortring(cur_is_mtc_file,title, 'NO VOLTE TUPLES ADDED, BUT HANDOVER FROM VOLTE TO VOWIFI')
		checkhasserrortring(cur_is_mtc_file,title, 'rejected (existing client(s) with higher priority)')
		checkhasserrortring(cur_is_mtc_file,title, 'JuIpsecServer: do_ip failed')
		checkhasserrortring(cur_is_mtc_file,title, 'VoWifiSecurityManager: Can not start attach as the current state is')
		checkhasserrortring(cur_is_mtc_file,title, '+CIREGU: 3,0')
		checkhasserrortring(cur_is_mtc_file,title, 'clearLoopMsgQueue: remove all of "Loop Message Queue"')
		checkhasserrortring(cur_is_mtc_file,title, 'SocketLastErr:Invalid argument')
		checkhasserrortring(cur_is_mtc_file,title, 'logined state call logout')
		checkhasserrortring(cur_is_mtc_file,title, 'RegRegingOnCimCnf try <6> times fail')
		checkhasserrortring(cur_is_mtc_file,title, 'state <AKA REQ PROC> run [TPT EAP MSG EAP FAILED]')
		checkhasserrortring(cur_is_mtc_file,title, 'Handover packets overview: fromcp=0')
		checkhasserrortring(cur_is_mtc_file,title, 'SocketLastErr:Address already in use')
		checkhasserrortring(cur_is_mtc_file,title, 'Could not open input file ring/RingBack.wav')
		checkhasserrortring(cur_is_mtc_file,title, 'SECURITY IKE: ERROR: TunnelCheckDpd Start Timer')
		checkhasserrortring(cur_is_mtc_file,title, 'zxsocket: RTNETLINK answers (Cannot assign requested address)')
		checkhasserrortring(cur_is_mtc_file,title, 'zxsocket: RTNETLINK answers (No such file or directory)')
		checkhasserrortring(cur_is_mtc_file,title, 'zxsocket: RTNETLINK answers (File exists)')
		
		checkhasserrortring(cur_is_mtc_file,title, 'Ping IP address is unreachable')		
		checkhasserrortring(cur_is_mtc_file,title, 'ACTION_DECLINE_INCOMING_CALL')
		checkhasserrortring(cur_is_mtc_file,title, 'ERROR: SendCmdToServer recvfrom')
		checkhasserrortring(cur_is_mtc_file,title, 'onProcessDpdDisconnectedError')
		checkhasserrortring(cur_is_mtc_file,title, 'ERROR: S2bDeleteIpsec bind socket errno')
		checkhasserrortring(cur_is_mtc_file,title, 'run [USER REGISTER] ignored event')		
		checkhasserrortring(cur_is_mtc_file,title, 'send buf list')
		checkhasserrortring(cur_is_mtc_file,title, 'EAP Code: Failure')
		checkhasserrortring(cur_is_mtc_file,title, 'reRegister->type: -1 info: 000000000000')
		checkhasserrortring(cur_is_mtc_file,title, '"MSG_HANDOVER_TO_VOLTE", mCurPendingProcessMsgId = "MSG_HANDOVER_TO_VOWIFI"')
		checkhasserrortring(cur_is_mtc_file,title, 'ERROR: socket bind failed')
		checkhasserrortring(cur_is_mtc_file,title, 'reg report register failed')
		checkhasserrortring(cur_is_mtc_file,title, 'ZOS: ERROR: PoolFree <zos memory> invalid redzone.')
		
		
		checksamevalue(cur_is_mtc_file, title, 'SECURITY IKE: INFO: Attribute: INTERNAL_IP6_ADDRESS ')

		checksamevalue(cur_is_mtc_file, title, 'ImsServiceImpl: getIMSRegAddress mImsRegAddress = ')
		 
		#checklogmissing(title, 'I liblog  :')

		
		title=f.readline(2048)
    f.close()
 

    
       
        

dir = 'E:\\LOG\\20160318-135756'  
dir = './'  
suffix = 'log'  


f = glob.glob(dir + '\\*.' + suffix)  
#print f 


for file in f :  
    filename = os.path.basename(file)  
    print file
    outputKey(file)        
    

