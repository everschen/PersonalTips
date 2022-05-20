#!/usr/bin/python
#coding:utf -8
 
import smtplib #smtp???
from email.mime.text import MIMEText #????
import sys
 

def send_email(title, content):

	if(title == None or content == None):
		print("parameters number error")
		exit(1)
	subject = title
	sender = "evers_chen@163.com"#???
	content = content
	recver = "evers_chen@163.com"#???
	#password = "cxg12345"
	password = "XQKTNSQQBFGOUZFE"
	message = MIMEText(content,"plain","utf-8")
	 
	message['Subject'] = subject #????
	message['To'] = recver #???
	message['From'] = sender #???
	 
	smtp = smtplib.SMTP_SSL("smtp.163.com",994) #???smtp???
	smtp.login(sender,password)#?????
	smtp.sendmail(sender,[recver],message.as_string()) #as_string ? message ????????
	smtp.close()
