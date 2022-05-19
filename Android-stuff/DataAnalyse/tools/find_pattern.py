
import glob,datetime,re
import ConfigParser
import string, os, sys
sys.path.append('./register') 
import utilities



 
cf = ConfigParser.ConfigParser()
cf.read(sys.path[0]+"\config.conf")
#cf.read("test.conf")
secs = cf.sections()
print 'Sections:', secs
print ""


utilities.handle_section(cf, 'main')
print ""

