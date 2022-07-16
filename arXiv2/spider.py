#coding=utf-8
import urllib.request
import time

from lxml import etree
import sys,os
import json, requests

sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../')
from common import sendmail


class arxiv_paper(object):
	def __init__(self,arxiv_id,title,author,subject):
		self.arxiv_id = arxiv_id
		self.title = title
		self.author = author
		self.subjects = subject
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


	def get_str(self):
		self.abstract = self.get_abstract(self.page)
		self.comments = self.get_comments(self.page)
		self.code = self.get_code()
		self.str = "\n---------------------------------------------------------\n\nTitle: %s\n\nComments: %s\n\nAuthors: %s\n\nSubjects:%s\n\nAbstract: %s\n\nPage: %s\n\nPDF: %s\n\nCode: %s\n\n"%(self.title,self.comments,self.author,self.subjects,self.abstract,self.page,self.PDF,self.code)
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


        
class arxiv_updater(object):
    def __init__(self, user_name:str, email:str, main_subject:str, second_subjects:list = None, key_words:list = None, n_show:int = 100):
        self.user_name = user_name
        self.email = email
        self.log_file = sys.path[0]+"/paper_log_%s.txt"%user_name
        self.main_subject = main_subject
        self.second_subjects = second_subjects
        self.key_words = key_words
        self.main_subject_url = "https://arxiv.org/list/%s/pastweek?show=%d"%(self.main_subject,n_show)
        self.paper_list = self.parse_arxiv()
        self.new_list = self.get_new()
        self.target_list = self.get_target_list()
    
    def parse_arxiv(self):
        self.index = self.get_html(self.main_subject_url,10)
        html_tree = etree.HTML(self.index)
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

    def get_html(self,url,err_count):
        request=urllib.request.Request(url)
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
    
    def get_new(self):
        new_list = []
        try:
            log = open(self.log_file,'r')
        except:
            log = open(self.log_file,'w')
            log.close()
            log = open(self.log_file,'r')
        history = log.read()
        log.close()
        for paper in self.paper_list:
            if paper.arxiv_id in history:
                continue
            else:
                paper.get_str()
                new_list.append(paper)
        log.close()

        return new_list

    def get_target_list(self):
        res_list = []
        for paper in self.new_list:
            flag = 0
            if self.second_subjects == None and self.key_words == None:
                res_list.append(paper)
                continue
            if self.second_subjects != None:
                for subject in self.second_subjects:
                    if subject in paper.subjects:
                        res_list.append(paper)
                        flag = 1
                        break
            if flag == 1:
                continue
            if self.key_words != None:
                for key_word in self.key_words:
                    if key_word in paper.str:
                        res_list.append(paper)
                        break
        return res_list

    def save_list(self,paper_list):
        log = open(self.log_file,'a')
        list_str = str([paper.arxiv_id for paper in paper_list]).replace('[','').replace(']',';').replace(', ',';')
        log.write(list_str)
        log.close()
        return 0



    def push(self):
        if len(self.target_list) == 0:
            print("无符合条件的更新")
            return 0
        content = ""
        for i in self.target_list:
            content = content+i.str
        if sendmail.SendMail(self.email,"arXiv推送小助手","arXiv今日定制论文",content):
            print("发送失败")
        else:
            print("发送成功:%s"%self.email)
            res = self.save_list(self.new_list)
            if res == 0:
                print("日志文件更新成功")




user1 = arxiv_updater("谢意", "454888912@qq.com", "cs.AI", key_words=["NLP","deep","learning","neural"], n_show = 100)
user1.push()

user2 = arxiv_updater("tbNick_egxfg", "3193727533@qq.com", "cs.AI", second_subjects=["cs.LG","stat.ML"], key_words=["privacy"], n_show = 100)
user2.push()

user3 = arxiv_updater("中国必胜2021", "1148510935@qq.com", "cs.AI", key_words=["few shot","contrastive learning","GAN","transformers","zero shot","zero-shot","few-shot"], n_show = 100)
user3.push()

user4 = arxiv_updater("伯牙不复鼓", "messiah@nuaa.edu.cn", "cs.AI", key_words=["NLP","deep","learning","neural"], n_show = 10)
user4.push()