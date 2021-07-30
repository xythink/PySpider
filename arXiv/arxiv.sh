source /home/xieyi/anaconda3/bin/activate base
proxychains python ~/code/PySpider/arXiv/spider_arxiv.py || (source /home/xieyi/anaconda3/bin/deactivate && bash ~/code/bark.sh arxiv小助手执行失败)
