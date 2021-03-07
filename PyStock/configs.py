"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-01-26 08:55
IDE: PyCharm
Introduction:
"""

import os
import configparser
from PyStock.utils import set_logger


config_file_path = os.path.abspath(__file__).replace(__name__.replace('.', "\\") + '.py' , '')

## 读取配置文件
cf = configparser.ConfigParser()
cf.read(os.path.join(config_file_path, 'config.ini'))

## 用户token信息
TS_TOKEN = cf.get('Account', 'token')
TS_SCORE = cf.getint('Account', 'score')

# ## 数据保存位置
PATH_GENERAL =  cf.get('File', 'general')
PATH_QUERY_DATA = os.path.join(PATH_GENERAL, cf.get('File', 'querydata'))

## 信息抓取配置
RETRY_TIMES = cf.getint('Spider', 'retry')
THREAD_NUMS = cf.getint('Spider', 'thread')

# ## 数据库信息
# DB_USERNAME =  cf.get('DBS', 'username')
# DB_PASSWORD =  cf.get('DBS', 'password')
# DB_DATABASE =  cf.get('DBS', 'database')

## 日志文件
logging_file = os.path.join(PATH_GENERAL, 'logging', 'logging.txt')
logger = set_logger(logging_file)