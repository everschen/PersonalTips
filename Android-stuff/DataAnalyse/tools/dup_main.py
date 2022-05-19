#/usr/bin/python
 
import ConfigParser
import string, os, sys

DEBUG = False
 
cf = ConfigParser.ConfigParser()
 
cf.read("config.conf")
 
#return all section
secs = cf.sections()
print 'sections:', secs

test_section = 'main' 
opts = cf.options(test_section)
print 'options:', opts
 

main_filter = cf.get(test_section, "filter").replace("\n", "")
#print main_filter

pats=main_filter.split('|')	
pats = [ x for x in pats if x != '' ]

need_add = ''
dup_pats = ''

for i in range(0, len(pats)):
	cur_pat = pats[i]
	#print cur_pat
	for j in range(i+1, len(pats)):
		if cur_pat == pats[j]:
			dup_pats = dup_pats + cur_pat + '|'
			break;



print ""

print ""
print ""
print ""
print ""
print ""
print dup_pats
'''
f=open('1.txt','a+')
f.write(need_add)
f.close()
'''


#############test#########################################
'''
section = 'main'
opts = cf.options(section)
if 'filter' in opts:
	print 'Process section',section, '...'
	cur_filter = cf.get(section, "filter").replace("\n", "")
	cur_pats=cur_filter.split('|')	
	cur_pats = [ x for x in cur_pats if x != '' ]
	for cur_pat in cur_pats:
		found =  False
		for main_pat in pats:
			if cur_pat in main_pat:
				found = True
				break

		if found == False:
			for main_pat in pats:
				if main_pat in cur_pat:
					#print cur_pat, "<-" , main_pat,
					found = True
					break
			if found == False:
				need_add = need_add + cur_pat + '|'
				print cur_pat, "not in main"
	print ""
'''
#############test#########################################