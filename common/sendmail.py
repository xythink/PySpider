#coding=utf-8  
import smtplib,datetime,os,sys
from email.mime.text import MIMEText  
from email.header import Header
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from readconfig import *
  


def SendMail(receivers,header,subject,m):
	
	  
	  
	sender = 'xieldy_push@qq.com'  
	  
	  
	message = MIMEText(m, 'plain', 'utf-8')  
	#message['From'] = Header("xieldy@qq.com", 'utf-8')  
	h = Header(header, 'utf-8')
	h.append('<xieldy_push@qq.com>', 'ascii')
	message['From'] = h
	
	message['To'] =  Header("you", 'utf-8')  

	
	    
	message['Subject'] = Header(subject, 'utf-8')  
	  
	try:  
		smtpObj = smtplib.SMTP_SSL(mail_host, 465)   
		smtpObj.login(mail_user,mail_pass)
		print("success!")    
		smtpObj.sendmail(sender, receivers, message.as_string())  
		smtpObj.quit()  
		print("Email send succeed!") 
		now = datetime.datetime.now()
		print(now.strftime('%Y-%m-%d %H:%M:%S'))
		print("----------------------------------------------------------------") 
		return 0
	except smtplib.SMTPException as e:  
	 	print(e[1].decode('gbk'))
	 	return 1 




