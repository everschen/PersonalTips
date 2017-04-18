# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:57:59 2016

@author: evers.chen
"""
import sys  
import glob  
import os  
import datetime
import re
import time
BUFLEN = 2048
FIND_PATTERN = False
#FIND_PATTERN = True
	
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

def regmatch(pat, source):
	p = re.compile(pat)
	if p.match(source):
		return True
	return False			
			
def add_line_to_file(source, filename, insert, is_mtc):
	str_len=18
	with open(filename, 'a+') as f:
		fff=open(filename)
		ff=fff.read()
		pos1 = ff.find(source)
		if pos1 != -1: # source already existed in the target file
			return

		#if '10:08:25.475 SIP: INFO:' in source:
			#print source,is_mtc, insert
			
		if is_mtc == True : #mtc file, need to sync time stamp
			#get the target date first, read from main.log
			main_f = open('main.log', 'r')
			for main_line in main_f:
				if regmatch('^[0-9][0-9]-[0-9][0-9] .*', main_line):
					target_date = main_line[0:6]
					break;
			source = target_date + source
			#if '10:08:25.475 SIP: INFO:' in source:
				#print source
				#print target_date
					
		lines = f.readlines()
		if len(lines) == 0 : #target file is empty
			file_object = open(filename, 'a+')
			file_object.write(source)
			file_object.close()
			return
			
		if insert.lower() == 'false' :	#append to target file		
			file_object = open(filename, 'a+')
			file_object.write(source)
			file_object.close()		
			return
					
		for i in range(0, len(lines)): 
			if cmp(lines[i][0:str_len],source[0:str_len]) > 0 :
				#if '02-16 16:48:46.021' in source:
					#print lines[i]
				lines.insert(i,source)
				open(filename, 'w').writelines(lines)
				return
			
		#print source, is_mtc, insert, filename, len(lines)
		if len(lines)-1 == i : #source time stamp is latest
			#if '02-16 17:23:26.599' in source:
				#print lines[i]
			file_object = open(filename, 'a+')
			file_object.write(source)
			file_object.close()
			return				
			
def add_line_to_files(title, filenames, sep, insert, is_mtc):
	files=filenames.split(sep)
	files = [ x for x in files if x != '' ]
	for file in files:
		add_line_to_file(title, file, insert, is_mtc)
		
def behindstr(source, pattern):
	pos1 = source.index(pattern)
	if pos1 == -1:
		print "not found pattern"
		return ""
	match='\n'
	pos2 = source.find(match,pos1)
	ret = source[pos1 + len(pattern):pos2]
	return ret

def checksamevalue(sep, source, equal_value, output, insert_mode, file, is_mtc):
	global last
	patterns=equal_value.split(sep)
	patterns = [ x for x in patterns if x != '' ]
	for pattern in patterns:	
		if pattern in source:
			#print pattern,"123"
			ret=behindstr(source, pattern)
			if ret != "" :
				#print pattern+ret
				current = item()
				current.source = source
				current.value = ret
				if 'mtc' in file:
					currenttime = source[0:8]
				else:
					currenttime = source[6:14]
				d1 = datetime.datetime.strptime(currenttime, '%H:%M:%S')
				current.time = d1
				delta = current.time - last.time
				if (delta.seconds > 15):
					last = current
				else:
					#print "delta",delta.seconds
					if (last.value.lower() != current.value.lower()):
						#print last.value.lower()
						#print current.value.lower()
						currenttime = '00:00:00'
						d1 = datetime.datetime.strptime(currenttime, '%H:%M:%S')
						last.time = d1	
						add_line_to_files(last.source, output,sep, insert_mode, is_mtc)						
						add_line_to_files(current.source,output,sep, insert_mode, is_mtc)

	
def reg_filter_pattern(sep, res_pattern, reg_pattern, source, output_file, insert_mode, is_mtc, trans_sep):		
	pats=reg_pattern.split(sep)
	pats = [ x for x in pats if x != '' ]
	if res_pattern == '' :
		res_pats = ''
	else:
		res_pats=res_pattern.split(sep)
		res_pats = [ x for x in res_pats if x != '' ]

	for pat in pats:
		if trans_sep != '' and trans_sep in pat: # if translation is there,need to update pat, and append translation later
			trans_pat = pat.split(trans_sep)
			pat = trans_pat[0]
			trans = trans_pat[1]
		else:
			trans = ''
			
		p = re.compile(pat)
		if p.match(source):
			if res_pats!='':
				for res_pat in res_pats:
					if res_pat in source:
						return 1;
						
			if trans != '' and trans_sep != '':#translation case
				#print pat,trans_sep,trans
				#new_pat = pat + '(' + trans +')'
				#source = source_case.replace(pat,new_pat)
				source = source.replace('\n', ' (' + trans +')\n')
			if FIND_PATTERN:
				print source,'<-',pat
			add_line_to_files(source, output_file, sep, insert_mode, is_mtc)
			return 0
	return 2

		
def filter_pattern(sep, res_pattern, pattern, source, output_file, case_sensitive, insert_mode, is_mtc, trans_sep):
	if pattern=='':
		return 2
	if case_sensitive.lower() == 'false':
		pattern = pattern.lower()
		res_pattern = res_pattern.lower()
		source_case = source.lower()
	else:
		source_case = source
		
	pats=pattern.split(sep)	
	pats = [ x for x in pats if x != '' ]
	if res_pattern == '' : 
		res_pats = ''
	else:
		res_pats=res_pattern.split(sep)
		res_pats = [ x for x in res_pats if x != '' ]

	for pat in pats:
		if trans_sep != '' and trans_sep in pat: # if translation is there,need to update pat, and append translation later
			trans_pat = pat.split(trans_sep)
			pat = trans_pat[0]
			trans = trans_pat[1]
		else:
			trans = ''
			
		if pat in source_case: #found pattern
			if res_pats!='':
				for res_pat in res_pats:
					if res_pat in source_case:
						return 1;
			if trans != '' and trans_sep != '':#translation case
				#print pat,trans_sep,trans
				#new_pat = pat + '(' + trans +')'
				#source = source_case.replace(pat,new_pat)
				source = source.replace('\n', ' (' + trans +')\n')
			if FIND_PATTERN:
				print source,'<-',pat
			add_line_to_files(source, output_file, sep, insert_mode, is_mtc)
			return 0
	return 2
    

def filter_file(section, input_file, output, sep, filter, case_sensitive, restrict_filter, regular_filter, insert_mode, equal_value,tran_sep):		
	input_files=input_file.split(sep)
	input_files = [ x for x in input_files if x != '' ]
	for input_file in input_files:
		f = glob.glob(input_file) 			
		for file in f :  
			filename = os.path.basename(file)
			current_file_is_mtc = False
			#print file
			if 'mtc' in filename:
				mtcf = glob.glob('mtc*') 				
				targetdate = mtcf[-1]
				#print targetdate
				date = targetdate[3:11]
				#print date				
				if date not in filename:
					continue
				current_file_is_mtc = True
			f=open(file, 'r')
			
			sys.stdout.write("Process section: " + section + " file: " + file+" -> " +output+" ")					
			total_lines = len(f.readlines())
			#print total_lines
			f.seek(0, 0)
			cur_line=f.readline(BUFLEN)
			i =1
			progress_last = 1
			
			while(cur_line):
				progress = i*100/total_lines
				if progress != progress_last:
					sys.stdout.write(str(progress)+'%')
					len_str = len(str(progress)) +1
					progress_last = progress
					while(len_str>0):
						sys.stdout.write("\b")
						len_str = len_str -1					
					sys.stdout.flush()
				
				if (filter_pattern(sep, restrict_filter, filter, cur_line, output, case_sensitive, insert_mode, current_file_is_mtc,tran_sep) == 2):
					if (regular_filter != ''):
						reg_filter_pattern(sep, restrict_filter, regular_filter, cur_line, output, insert_mode, current_file_is_mtc,tran_sep)
					if (equal_value != ''):
						checksamevalue(sep, cur_line, equal_value, output, insert_mode, file, current_file_is_mtc)
				cur_line=f.readline(BUFLEN)
				i = i+1
			f.close()
			print ""

	
def handle_section(cf, section):
	options = ['input','output','filter_sep','filter','case_sensitive','restrict_filter', 'regular_filter', 'insert_mode','equal_value_check','translate_sep']
	Val = {}
	opts = cf.options(section)
	
	for support_opt in options:
		if support_opt in opts:
			Val[support_opt] = cf.get(section, support_opt).replace("\n", "")
		elif support_opt=='filter_sep':
			Val[support_opt] = '|'
		elif support_opt =='translate_sep':
			Val[support_opt] = '<-'
		else:
			Val[support_opt] = ''
	filter_file(section,Val['input'],Val['output'],Val['filter_sep'],Val['filter'],Val['case_sensitive'],
		Val['restrict_filter'],Val['regular_filter'],Val['insert_mode'],Val['equal_value_check'],Val['translate_sep'])
	


	
	
	
