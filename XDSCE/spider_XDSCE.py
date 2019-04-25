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
	url = 'http://ce.xidian.edu.cn/info/1021/%s.htm'%str(num)
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
	title = re.search(r'<TITLE>(.*?)-西安电子科技大学网络与信息安全学院</TITLE>',html).group(1)
	time = re.search(r'<span>发布时间:(.+?)</span>',html).group(1)
	tmp = re.search(r'class="detail">(.+?)id="div_vote_id"></div>',html,flags=re.DOTALL+re.MULTILINE).group(1)
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
		log = open(sys.path[0]+'/XDSEC_info.txt','r')
	except:
		log = open(sys.path[0]+'/XDSEC_info.txt','w')
		log.close()
		log = open(sys.path[0]+'/XDSEC_info.txt','r')
	history = log.read()
	log.close()
	print(history)
	url = 'http://ce.xidian.edu.cn/tzgg.htm'
	request = urllib.request.Request(url)
	try:
		response = urllib.request.urlopen(request)
		content = response.read().decode('utf-8')
	except:
		print("无法获得通知列表！")
		return 1
	info_list = re.findall(r'<A href="info/1021/(.*?)\.htm',content)
	log = open(sys.path[0]+'/XDSEC_info.txt','a')
	for i in info_list:
		if i in history:
			continue
		else:
			log.write('%s;'%(i))
			GetHtml(i)
			res = Catch(sys.path[0]+'/log'+'/%s.html'%i)
			#if pushover.SendWX(res["title"],res["time"]+'\n'+res["detail"],url='http://ce.xidian.edu.cn/info/1021/%s.htm'%i):
			url='http://ce.xidian.edu.cn/info/1021/%s.htm'%i
			if sendmail.SendMail("454888912@qq.com","西电网信院",res["title"],res["time"]+'\n'+res["detail"]+'\n'+url):
				print("发送失败")
			else:
				print("发送成功")
	log.close()
	return 0

			

Update()


