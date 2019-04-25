#coding=utf-8  
import smtplib,datetime
from email.mime.text import MIMEText  
from email.header import Header  

  


def SendMail(receivers,header,subject,m):
	# 第三方 SMTP 服务  
	mail_host="smtp.qq.com"  #设置服务器  
	mail_user="xieldy_push@qq.com"    #用户名  
	mail_pass="ksbivffxorebhcih"   #口令,QQ邮箱是输入授权码，在qq邮箱设置 里用验证过的手机发送短信获得，不含空格  
	  
	  
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



#thjjhjzavpodbjfc
#ttvxdyilquhgbhfb
#gpbmgsffhghabjad
