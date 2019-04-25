#coding=utf-8
import urllib.request,re
import sys,os

sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../')
from common import sendmail

def showresult(func):
	def wrapper(*argv,**kwargvs):
		res = func(*argv,**kwargvs)
		print("The function[%s]'s result is :  %s"%(func.__name__,res))
		return res
	return wrapper

@showresult
def GetHtml(num):
	url = 'https://gr.xidian.edu.cn/info/1081/%s.htm'%str(num)
	print(url)
	request = urllib.request.Request(url)
	try:
		response = urllib.request.urlopen(request)
		content = response.read()
	except:
		return 1
	html_save = open(sys.path[0]+'/log'+'/%s.html'%num,'wb')
	html_save.write(content)
	html_save.close()
	return 0

@showresult
def Catch(filename):
	html_save = open(filename,'r')
	html = html_save.read()
	html_save.close()
	title = re.search(r'<div class="content-bt">(.*?)</div>',html).group(1)
	time = re.search(r'<span>发布时间：(.+?)</span>',html).group(1)
	tmp = re.search(r'class="v_news_content">(.+?)id="div_vote_id"></div>',html,flags=re.DOTALL+re.MULTILINE).group(1)
	detail = re.sub(r'<[^>]+>','',tmp)
	detail = re.sub(r'&nbsp','',detail)
	detail = re.sub(r'<div','',detail)
	detail = re.sub(r'[\s]+','\n',detail)
	print(detail)
	res = {
		"title": title,
		"time": time,
		"detail": detail,
	}
	return res


def Update():
	print(sys.path[0])
	try:
		log = open(sys.path[0]+'/XDYJS_info.txt','r')
	except:
		log = open(sys.path[0]+'/XDYJS_info.txt','w')
		log.close()
		log = open(sys.path[0]+'/XDYJS_info.txt','r')
	history = log.read()
	log.close()
	print(history)
	url = 'https://gr.xidian.edu.cn/zxdt.htm'
	request = urllib.request.Request(url)
	try:
		response = urllib.request.urlopen(request)
		content = response.read().decode('utf-8')
	except:
		print("无法获得通知列表！")
		return 1
	info_list = re.findall(r'<a href="info/1081/(.*?)\.htm',content)
	log = open(sys.path[0]+'/XDYJS_info.txt','a')
	for i in info_list:
		if i in history:
			continue
		else:
			log.write('%s;'%(i))
			GetHtml(i)
			res = Catch(sys.path[0]+'/log'+'/%s.html'%i)
			#if pushover.SendYJS(res["title"],res["time"]+'\n'+res["detail"],url='https://gr.xidian.edu.cn/info/1081/%s.htm'%i):
			url='https://gr.xidian.edu.cn/info/1081/%s.htm'%i
			if sendmail.SendMail("454888912@qq.com","西电研究生",res["title"],res["time"]+'\n'+res["detail"]+'\n'+url):
				print("发送失败")
			else:
				print("发送成功")
	log.close()
	return 0

			



"""
def Update():
	log = open('XDSEC.txt','r')
	history_num = int(log.read())
	log.close()
	num = history_num + 1
	while GetHtml(num)==0:
		print("----------------------------")
		log = open('XDSEC.txt','w')
		log.write(str(num))
		log.close()
		res = Catch('%s.html'%num)
		url = 'http://ce.xidian.edu.cn/info/1021/%s.htm'%str(num)
		if pushover.Send(res+'\n原文地址：%s'%url):
			print("发送失败")
		else:
			print("发送成功")
		num = num + 1
	return 0
"""
Update()


