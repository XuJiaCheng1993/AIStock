"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-01-22 16:57
IDE: PyCharm
Introduction:
"""
import os
import tushare as ts
import pandas as pd

from PyStock.configs import TS_TOKEN
from PyStock.crawler import multiThreadQuery, onceQuery
from PyStock import runGeneralQuery
import json

ts.set_token(TS_TOKEN)

# oq = onceQuery(interface='gz_index')
# oq.run()



# mtq = multiThreadQuery(interface='fina_indicator', target_field='ts_code')
# mtq.run()
#
# #
# pro = ts.pro_api()
# #
# df = pro.query('shibor')
# df2 = pro.query('shibor', end_date='20130107')
#
# mtq = runGeneralQuery(interface='daily')
#
mtq = multiThreadQuery(interface='balancesheet', target_field='ts_code')
mtq.run(retry=20)

# from PyStock.infos.heads import info_interface
#
#
#
# head = info_interface('daily_basic')
# ','.join(head['head'].keys())

