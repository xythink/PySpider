#coding=utf-8
import os,sys

file_dir = os.path.dirname(os.path.abspath(__file__))

config_path = file_dir+'/../../pyspider_conf'
config_file = file_dir+'/../../pyspider_conf/config.py'
default_file = file_dir+'/default_config.py'



def new_conf(f):
	default = open(default_file)
	tmp = default.read()
	f.write(tmp)
	f.close()
	print("缺少配置文件，已经生成默认文件，请修改相关配置")
	sys.exit(0)
	return 0



if os.path.exists(config_file):
	pass
elif os.path.exists(config_path):
	f = open(config_file,'w+')
	new_conf(f)
	

else:
	os.makedirs(config_path)
	f = open(config_file,'w+')
	new_conf(f)

sys.path.append(config_path)
from config import *


