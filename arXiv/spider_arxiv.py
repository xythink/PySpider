#coding=utf-8
import urllib.request
import time

from lxml import etree
import sys,os
import json, requests

sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../')
from common import sendmail

def showresult(func):
	def wrapper(*argv,**kwargvs):
		print("Start function[%s]"%func.__name__)
		res = func(*argv,**kwargvs)
		print("The function[%s] end, result:%s"%(func.__name__,res))
		return res
	return wrapper

class arxiv_paper(object):
	def __init__(self,arxiv_id,title,author,subject):
		self.arxiv_id = arxiv_id
		self.title = title
		self.author = author
		self.subject = subject
		self.page = "https://arxiv.org/abs/"+self.arxiv_id
		self.PDF = "https://arxiv.org/pdf/"+self.arxiv_id+".pdf"
		self.html = None
		self.tree = None
		
	def get_abstract(self,url):
		self.html = self.get_html(url,10)
		self.tree = etree.HTML(self.html)
		abs_path = self.tree.xpath('//blockquote[@class="abstract mathjax"]')[0]
		abs = abs_path.xpath('string(.)').strip().replace("\n",'').replace("Abstract: ","")
		return abs

	def get_comments(self, url):
		if self.html == None:
			self.html = self.get_html(url,10)
		if self.tree == None:
			self.tree = etree.HTML(self.html)
		comments_list = self.tree.xpath('//td[@class="tablecell comments mathjax"]')
		if len(comments_list) > 0:
			return comments_list[0].xpath('string(.)')
		else:
			return 'None'
	
	def get_code(self):
		url = "https://arxiv.paperswithcode.com/api/v0/repos-and-datasets/%s"%self.arxiv_id
		response = requests.get(url)
		js = json.loads(response.text)
		if js['status'] != 'OK':
			return 'None'
		if js['code']['official'] != None:
			return js['code']['official']['url']
		else:
			return 'None'
		

	#@showresult
	def get_str(self):
		self.abstract = self.get_abstract(self.page)
		self.comments = self.get_comments(self.page)
		self.code = self.get_code()
		self.str = "\n---------------------------------------------------------\n\nTitle: %s\n\nComments: %s\n\nAuthors: %s\n\nSubjects:%s\n\nAbstract: %s\n\nPage: %s\n\nPDF: %s\n\nCode: %s\n\n"%(self.title,self.comments,self.author,self.subject,self.abstract,self.page,self.PDF,self.code)
		return self.str

	
	def get_html(self,url,err_count):
		request  =urllib.request.Request(url)
		try:
			response = urllib.request.urlopen(request)
			content = response.read()#.decode('utf-8')
		except:
			if err_count <= 0:
				raise TimeoutError
			err_count -= 1
			print("url解析错误，5秒后重新尝试！\n",url)
			time.sleep(5)
			content = self.get_html(url,err_count)
		return content

class arXiv_spider(object):
	def __init__(self,url):
		self.url = url
		self.index = self.get_html(url,10)
		self.html_tree = etree.HTML(self.index)
		self.paper_list = self.parse_arxiv(self.html_tree)
		self.log_file = sys.path[0]+"/paper_log.txt"
		self.new_list = self.get_new(self.paper_list)

	
	def get_html(self,url,err_count):
		request  =urllib.request.Request(url)
		try:
			response = urllib.request.urlopen(request)
			content = response.read()#.decode('utf-8')
		except:
			if err_count <= 0:
				raise TimeoutError
			err_count -= 1
			print("url解析错误，5秒后重新尝试！\n",url)
			time.sleep(5)
			content = self.get_html(url,err_count)
		return content
	
	def parse_arxiv(self,html_tree):
		id_path = html_tree.xpath('//a[@title="Abstract"]/text()')
		id_list = []
		for i in id_path:
			id = i.replace("arXiv:",'')
			id_list.append(id)

		title_path = html_tree.xpath('///div[@class="list-title mathjax"]')
		title_list = []
		for i in title_path:
			title = i.xpath('string(.)').strip().replace("Title: ",'')
			title_list.append(title)

		author_path = html_tree.xpath('//div[@class="list-authors"]')
		author_list = []
		for i in author_path:
			author = i.xpath('string(.)').replace('\n','').replace('Authors: ','')
			author_list.append(author)
			
		subject_path = html_tree.xpath('//div[@class="list-subjects"]')
		subject_list = []
		for i in subject_path:
			subject = i.xpath('string(.)').strip().replace("Subjects: ",'')
			subject_list.append(subject)

		num_papers = len(id_list)
		paper_list = []

		for i in range(num_papers):
			paper_id = id_list[i]
			paper_title = title_list[i]
			paper_author = author_list[i]
			paper_subject = subject_list[i]
			paper = arxiv_paper(paper_id,paper_title,paper_author,paper_subject)
			paper_list.append(paper)
		
		return paper_list


	#@showresult
	def get_target_list(self,subject,origin_list = None):
		res_list = []
		if origin_list == None:
			origin_list = self.paper_list
		for paper in origin_list:
			for i in subject:
				if i in paper.subject:
					res_list.append(paper)
					break
		return res_list
	
	#@showresult
	def get_new(self,paper_list):
		new_list = []
		try:
			log = open(self.log_file,'r')
		except:
			log = open(self.log_file,'w')
			log.close()
			log = open(self.log_file,'r')
		history = log.read()
		log.close()
		for paper in paper_list:
			if paper.arxiv_id in history:
				continue
			else:
				new_list.append(paper)
		log.close()

		return new_list

	def save_list(self,paper_list):
		log = open(self.log_file,'a')
		list_str = str([paper.arxiv_id for paper in paper_list]).replace('[','').replace(']',';').replace(', ',';')
		log.write(list_str)
		log.close()
		return 0
	
	def push(self,subject=None):
		if subject == None:
			push_list = self.new_list
		else:
			push_list = self.get_target_list(subject,self.new_list)
		if len(push_list) == 0:
			print("无符合条件的更新")
			return 0
		content = ""
		for i in push_list:
			content = content+i.get_str()
		if sendmail.SendMail("yixie1997@gmail.com","arXiv推送小助手","arXiv今日AI安全论文",content):
			print("发送失败")
		else:
			print("发送成功")
			res = self.save_list(self.new_list)
			if res == 0:
				print("日志文件更新成功")



		

spider = arXiv_spider("https://arxiv.org/list/cs.CR/pastweek?show=100")
spider.push(["cs.LG","stat.ML","cs.AI"])

