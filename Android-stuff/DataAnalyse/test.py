#/usr/bin/python
 
import ConfigParser
import string, os, sys
 
def remove_empty(list):
	for s in list:
		if s == '':
			list.remove(s)
	return list
	
	
a = ['ddd','e','p']
print a

a = [ x for x in a if x != '' ]
print a