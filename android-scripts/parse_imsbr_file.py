#Try to analysis the handover related problems. But I'm not clever enough as you
#expected, so need your help to let me know more things :(
#
#Author: liping.zhang@spreadtrum.com

import sys
import re
import glob
import os  

class imsbr_parser:
	recv_packets = 0 # packets received from cp side
	send_packets = 0 # packets send to cp side
	vowifi_tuples = 0
	volte_tuples = 0
	last_ho_state = "ho-finish"

	parser_list = []

	def __init__(self, regex):
		self.pattern = re.compile(regex)
		imsbr_parser.parser_list.append(self)

	def checkit(self, time, match):
		pass

	def parse(self, time, line):
		match = self.pattern.search(line)
		if match:
			self.checkit(time, match)
			return True
		else:
			return False

			
			
			
def add_line_to_file(title, filename, insert):
    str_len=18
    title = title + '\n'
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
    		file_object.write(title[1:])
    		file_object.close()
    		return
			
		
    	for i in range(0, len(lines)):
    		#print "i="+str(i)
    		#print "p1:"+lines[i]
    		#print "p2:"+lines[i][0:str_len]
    		#print "p3:"+title[0:str_len]
    		if cmp(lines[i][0:str_len],title[1:str_len]) > 0 :
    			#print "pos2"
    			lines[i:1] = [title[1:]]
    			open(filename, 'w').writelines(lines)
    			return
    		else:
    			#print "pos1"
    			continue

		
    	#print len(lines),i
    	if len(lines)-1 == i :
    		#print len(lines),i
    		file_object = open(filename, 'a+')
    		file_object.write(title[1:])
    		file_object.close()
    		return				
				
		#open(cfg_sa, 'w').writelines(lines)
		

			
			
class imsbr_tuple_parser(imsbr_parser):
	'''
	Format:
	c2 imsbr: volte-add(sip) l3=41 l4=50 fd00:0:5:1::1 0 -> fd00:0:20:1::20 0	
	'''
	def __init__(self, regex = " c\d imsbr: (volte|vowifi)-(add|del)(.*)"):
		imsbr_parser.__init__(self, regex)

	def checkit(self, t, m):
		if m.group(1) == "volte":
			if m.group(2) == "add":
				imsbr_parser.volte_tuples += 1
			else:
				imsbr_parser.volte_tuples -= 1
		else:
			if m.group(2) == "add":
				imsbr_parser.vowifi_tuples += 1
			else:
				imsbr_parser.vowifi_tuples -= 1

		add_line_to_file(t +"  "+m.group(1) + " " + m.group(2) + m.group(3),'imsbr.log', 0) 

class imsbr_callstate_parser(imsbr_parser):
	'''
	Format:
	c0 imsbr: call switch to [volte] init=volte curr=volte ho=ho-finish->ho-finish
	'''
	def __init__(self, regex = " c\d imsbr: call switch to \[(.*)\]"):
		imsbr_parser.__init__(self, regex)

	def checkit(self, t, m):
		add_line_to_file(t + "  Start " + m.group(1) + " call", 'imsbr.log', 0) 

class imsbr_handover_parser(imsbr_parser):
	'''
	Format:
	c0 imsbr: trigger handover [ho-lte2wifi]
	'''
	def __init__(self, regex = " c\d imsbr: trigger handover \[(.*)\]"):
		imsbr_parser.__init__(self, regex)

	def checkit(self, t, m):
		ho = m.group(1)
		add_line_to_file(t + "  "+ "Trigger" + "  "+ho, 'imsbr.log', 0) 
		if ho == "ho-finish":
			fromcp = imsbr_parser.recv_packets
			tocp = imsbr_parser.send_packets
			imsbr_parser.recv_packets = 0
			imsbr_parser.send_packets = 0

			add_line_to_file( t+ "  "+  "!!!---Handover packets overview: fromcp=%d, tocp=%d" %(fromcp, tocp), 'imsbr.log', 0) 

			if imsbr_parser.last_ho_state == "ho-lte2wifi":
				if fromcp == 0:
					add_line_to_file(t+ " @@@@NO PACKETS FROM CP, NEED CP CHECK IT FIRST@@@@", 'imsbr.log', 0) 
				elif tocp == 0:
					add_line_to_file(t+ " @@@@NO PACKETS RECV FROM WIFI, MAYBE IP CHANGED, SECURITY CHECK IT FIRST@@@@", 'imsbr.log', 0) 

		elif ho == "ho-wifi2lte":
			if imsbr_parser.vowifi_tuples < 1:
				add_line_to_file(t+ " @@@@NO VOWIFI TUPLES ADDED, BUT HANDOVER FROM VOWIFI TO VOLTE@@@@", 'imsbr.log', 0)
		elif ho == "ho-lte2wifi":
			if imsbr_parser.volte_tuples < 1:
				add_line_to_file(t+  " @@@@NO VOLTE TUPLES ADDED, BUT HANDOVER FROM VOLTE TO VOWIFI@@@@", 'imsbr.log', 0)

		imsbr_parser.last_ho_state = ho

class imsbr_recvpacket_parser(imsbr_parser):
	'''
	Format:
	c0 imsbr: process packet from cp: src=2405:204:1a09:c645::9f7:e8b0 dst=2405:200:330:1587::10 ...
	'''
	def __init__(self, regex = " c\d imsbr: process packet from cp:"):
		imsbr_parser.__init__(self, regex)

	def checkit(self, t, m):
		imsbr_parser.recv_packets += 1

class imsbr_recvpkts_parser(imsbr_parser):
	'''
	Format:
	c0 imsbr_process_packet: 304 callbacks suppressed
	'''
	def __init__(self, regex = " c\d imsbr_process_packet: (\d+) callbacks suppressed"):
		imsbr_parser.__init__(self, regex)

	def checkit(self, t, m):
		imsbr_parser.recv_packets += int(m.group(1))

class imsbr_sendpacket_parser(imsbr_parser):
	'''
	Format:
	c0 imsbr: relay packet to cp: src=2405:200:330:1587::10 dst=2405:204:1a09:c645::9f7:e8b0 ...
	'''
	def __init__(self, regex = " c\d imsbr: relay packet to cp: "):
		imsbr_parser.__init__(self, regex)

	def checkit(self, t, m):
		imsbr_parser.send_packets += 1

class imsbr_sendpkts_parser(imsbr_parser):
	'''
	Format:
	c0 imsbr_packet_relay2cp: 304 callbacks suppressed
	'''
	def __init__(self, regex = " c\d imsbr_packet_relay2cp: (\d+) callbacks suppressed"):
		imsbr_parser.__init__(self, regex)

	def checkit(self, t, m):
		imsbr_parser.send_packets += int(m.group(1))

if __name__ == '__main__':
	dir = '../kernel/'  
	suffix = 'log'  
	f = glob.glob(dir + '\\*.' + suffix)  
	print f 


	for file in f :  
		filename = os.path.basename(file)  
		print file
  
	
		imsbr_tuple_parser()
		imsbr_callstate_parser()
		imsbr_handover_parser()
		imsbr_recvpacket_parser()
		imsbr_recvpkts_parser()
		imsbr_sendpacket_parser()
		imsbr_sendpkts_parser()

		imsbr_tuple_parser()
		imsbr_callstate_parser()
		imsbr_handover_parser()
		imsbr_recvpacket_parser()
		imsbr_recvpkts_parser()
		imsbr_sendpacket_parser()
		imsbr_sendpkts_parser()

		try:
			f = open(file, "r")
		except IOError, e:
			print "Open fail:", e
			sys.exit(1)

		for line in f:
			if " imsbr" not in line:
				continue

			#Format: 01-01 08:04:05.743 ...
			t = line.split()
			t = t[0] + " " + t[1]

			for p in imsbr_parser.parser_list:
				if p.parse(t, line):
					break
