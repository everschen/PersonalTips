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
		



           
  

    
def outputKey(filename):
    num=0
	
    if "main" in filename:
    	insert=0
    elif "radio" in filename:
    	insert=1
    elif "imsbr" in filename:
    	insert=88
    elif "mtc" in filename:
    	return		
    elif "system" in filename:
    	return
    else:
    	insert=3
    print insert,filename

	
    f=open(filename)
    title=f.readline()
    while(title):
		if "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "ImsCall : start" in title or "Initiates an ims call with" in title or "onImsPdnStatusChange" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title or "blankblankblankblank" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "startVoWifiCall" in title or "startVoLteCall" in title or "Reset the security and sip stack with wifi state" in title or "Cellular network is not available" in title or "Can't switch calls" in title or "MRF: DEBUG: EndpGetActReg Reg is not exist." in title or "Show Dialog: Can't call" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue			
		if insert == 88:			
			add_line_to_file(title,'system_behavior.txt', 1)				
			title=f.readline()
			continue	
		if "imsbr   : set call state vowifi-call" in title or "EVENT_UPDATE_DATA_ROUTER_FINISHED" in title or "SECURITY IKE: INFO:   Next Payload: Configuration" in title or "SECURITY IKE: INFO:  Notify Message Type: INITIAL_CONTACT" in title or "Handle the event 'call_terminate' for the call" in title or "ImsCall : callSessionTerminated" in title or "ImsCall : processCallTerminated" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue			
		if "IKE: INFO: DNS query record<A> ok." in title or "DNS: INFO: SendQryReq primary dns server" in title or "PingHelper: execute command start : ping" in title or "ImsServiceImpl: getIMSRegAddress mImsRegAddress =" in title or "SECURITY IKE: INFO: SessDnsLookUp" in title or "SessFqdnIpv6OnDns" in title or "TunnelCheckDpd" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue			
		if "InCall  : CallerInfoAsyncQuery - - number:" in title or "InCall  : CallerInfoAsyncQuery - - cookie:" in title or "loopProcessAudioQos" in title or "del vowifi tuple" in title or "add vowifi tuple" in title or "Mrf_RegRemoveExpiredIpsec" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "ImsVideoCallProviderImpl: On set the camera from front to null" in title or " SecurityS2bBinder: INFO: notifyNetChange true" in title or "SessAuthOnResendTmr" in title or "Ike ResendTimer MsgId" in title or "Ike Config Not Support Mobike" in title or "Ike epdg Not support Mobike" in title or "InCall  : CallCardPresenter - Disconnecting" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "RegisterService: Try to reset the sip stack." in title or "RegisterService: Try to start the de-register process" in title or "MRF: INFO: subs process [USER UNSUBSCRIBE]" in title or "MRF: INFO: endpoint process [USER UNREGISTER]" in title or "Mrf_RegUnregingOnTeWaitU" in title or "Mrf_RegTearDownSa" in title or "SprocOn" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue	
		if "SECURITY IKE: INFO: Attribute: INTERNAL_IP6_ADDRESS" in title or "calculateQosAverage: mQosLossAverage" in title or "calculateQosAverage: mQosJitterAverage" in title or "calculateQosAverage: mQosLatencyAverage" in title or "calculateSignalAverage: mWifiRssiAverage" in title or "calculateSignalAverage: mLteRsrpAverage" in title or "calculateSignalAverage: mQosWifiRssiAverage" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue			
		if "ImsServiceImpl: setIMSRegAddress addr =" in title or "MTC: DEBUG: client reg state" in title or "MRF: INFO: endpoint process [USER REGISTER]" in title or "MRF: INFO: RegListenLocally security" in title or "Mrf_RegAddIpsecSA" in title or "Mrf_RegRmvIpsecSA" in title or "SECURITY IKE: INFO: Attribute: INTERNAL_IP4_ADDRESS" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "ImsServiceImpl: getIMSRegAddress mImsRegAddeess =" in title or "SECURITY IKE: INFO:   Type Payload: Delete" in title or "D LEMON   : SIP/2.0" in title or "MME     : ERROR" in title or "SprocOnCallEvnt" in title or "VoWifiSerService" in title or "SECURITY IKE: INFO: Ike_MsgDump PayLd:(1)Delete" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue		
		if "EVENT_WIFI_NETWORK_DISCONNECTED" in title or "VoWifiRegisterManager" in title or "RegisterServiceBinder" in title or "VoWifiManager" in title or "D LEMON   : REGISTER sip:" in title or "D LEMON   : SIP/2.0 200 OK" in title or "D LEMON   : SUBSCRIBE sip:" in title or "D LEMON   : NOTIFY sip:" in title or "D LEMON   : SIP/2.0 401 Unauthorized" in title:
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)
			title=f.readline()
			continue
		if "EVENT_WIFI_NETWORK_CONNECTED" in title or "D LEMON   : INVITE sip:" in title or "D LEMON   : SIP/2.0 100 Trying" in title or "D LEMON   : SIP/2.0 183 Session Progress" in title or "D LEMON   : UPDATE sip:" in title or "D LEMON   : ACK sip:" in title or "D LEMON   : BYE sip:" in title or "VowifiServiceCallback" in title or "ImsVoWifiService" in title:
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "VoWifiSecurityS2bManager" in title or "I S2b     :" in title:
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "[IKE] sending DELETE for IKE_SA android" in title or "[IKE] initiating IKE_SA android" in title or "[ENC] generating IKE_SA_INIT request" in title or "[ENC] generating IKE_AUTH request" in title or "[IKE] authentication of 'IMS' with EAP successful" in title or "[IKE] ireton-获得ip地址-" in title or "[IKE] ireton-获得pcscf地址-" in title:
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue			
		if "D LEMON   : SIP/2.0 503 Service Unavailable" in title or "D imsbr   : add vowifi tuple" in title or "I System.out:" in title or "ImsConnectionManagerService" in title or "D LEMON   : SIP/2.0 180 Ringing" in title or "D LEMON   : PRACK sip:" in title or "SecurityS2bCallback" in title or "[DMN] successfully created TUN" in title or "SIM MCC/MNC is" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "+IMSREGADDR" in title or "^CONN" in title or "AT+CHLD=" in title or "+CIREG" in title or "+IMSHO" in title or "+VOWFREG" in title or "+IMSWFATT" in title or "+IMSHOWFINF" in title or "+IMSHOCALLEND" in title or "+VOWIFIEN" in title or "^DSCI:" in title or "+IMSEN" in title or "RIL_REQUEST_ENABLE_IMS" in title or "+IMSHOLTEINFU" in title or "+VOWIFISRV" in title or "+IMSHODATAROUTER=1" in title:
			
			if insert!=1:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "WIFIPARAM" in title or "WIFIPARAM" in title or "WIFIPARAM" in title or "WIFIPARAM" in title or "WIFIPARAM" in title or "+IMSHODATAROUTER=1" in title:
	
			if insert!=1:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue			
		if "ImsCMUtils" in title:
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "EVENT_WIFI_ATTACH_FAILED" in title or "EVENT_WIFI_ATTACH_STOPED" in title or "EVENT_WIFI_ATTACH_SUCCESSED" in title or "failed to setup TUN device" in title or "imsbr   : add vowifi tuple" in title or "Start vowifi call, now attach rules" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "imsbr   : del vowifi tuple" in title or "volteRegistered:true" in title or "mWifiRegistered:true" in title or "data router" in title or "volteip" in title or "EVENT_WIFI_ALL_CALLS_END" in title or "Zos_ImsbrdEndCall" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "Zos_ImsbrdStartVowifiCall" in title or "Zos_ImsbrdStartVoLTECall" in title or "Zos_ImsbrdResetTuple" in title or "Start the audio for input and output" in title or "Stop the audio for input and output" in title or "can not re-register with empty info which used to handover" in title or "ZOS: INFO: Client" in title:			
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "SECURITY IKE: INFO: Ike ResendTimer MsgId:5 Resend" in title or "SECURITY IKE: INFO: SessAuthOnResendTmr Dpd Resend Timeout" in title or "Imsbrd enable vrt ok." in title or "ZOS: INFO: SocketLastErr:Invalid argument" in title or "ZOS: ERROR: sendto error" in title or "D LEMON   : SIP/2.0 404 " in title or "MTC: ERROR: imei format is not correct!" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
		if "RRE: DEBUG: reg report" in title or "Get the service logout callback" in title or "Get the register state changed callback" in title or "Get the security callback" in title or "ACTION_START_HANDOVER-> mFeatureSwitchRequest is exist" in title or "ImsCM Utils" in title or "SECURITY IKE: INFO:  Notify Message Type: AUTHENTICATION_FAILED" in title:			
			#print title
			
			if insert!=0:
				add_line_to_file(title+filename,'system_behavior_missing.txt', 0)
			else:
				add_line_to_file(title,'system_behavior.txt', insert)				
			title=f.readline()
			continue
			
		title=f.readline()
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
    

