#coding=utf-8
import urllib.request
import time
from lxml import etree
import sys,os

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
		
	def get_abstract(self,url):
		html = self.get_html(url)
		tree = etree.HTML(html)
		abs_path = tree.xpath('//blockquote[@class="abstract mathjax"]')[0]
		abs = abs_path.xpath('string(.)').strip().replace("\n",'').replace("Abstract: ","")
		return abs

	#@showresult
	def get_str(self):
		self.abstract = self.get_abstract(self.page)
		self.str = "\n---------------------------------------------------------\n\nTitle: %s\n\nAuthors: %s\n\nSubjects:%s\n\nAbstract: %s\n\nPage: %s\n\nPDF: %s\n\n"%(self.title,self.author,self.subject,self.abstract,self.page,self.PDF)
		return self.str

	
	def get_html(self,url):
		request  =urllib.request.Request(url)
		try:
			response = urllib.request.urlopen(request)
			content = response.read()#.decode('utf-8')
		except:
			print("url解析错误，5秒后重新尝试！\n",url)
			time.sleep(5)
			content = self.get_html(url)
		return content

class arXiv_spider(object):
	def __init__(self,url):
		self.url = url
		self.index = self.get_html(url)
		self.html_tree = etree.HTML(self.index)
		self.paper_list = self.parse_arxiv(self.html_tree)
		self.log_file = sys.path[0]+"/paper_log.txt"
		self.new_list = self.get_new(self.paper_list)

	
	def get_html(self,url):
		request  =urllib.request.Request(url)
		try:
			response = urllib.request.urlopen(request)
			content = response.read()#.decode('utf-8')
		except:
			print("url解析错误，5秒后重新尝试！\n",url)
			time.sleep(5)
			self.get_html(url)
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
		log = open(self.log_file,'a')
		for paper in paper_list:
			if paper.arxiv_id in history:
				continue
			else:
				log.write("%s;"%paper.arxiv_id)
				new_list.append(paper)
		log.close()

		return new_list
	
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



		

spider = arXiv_spider("https://arxiv.org/list/cs.CR/pastweek?show=100")
spider.push(["cs.LG","stat.ML","cs.AI"])

