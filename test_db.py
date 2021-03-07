"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-02-04 10:23
IDE: PyCharm
Introduction:
"""

import os
import pandas as pd
import tushare as ts
from PyStock.configs import TS_TOKEN, PATH_QUERY_DATA
from PyStock.infos import info_interface
from PyStock.dbs import BaseDB
import numpy as np


interface = 'fina_indicator'
print(','.join(info_interface(interface)['head'].keys()))
data = pd.read_csv(os.path.join(PATH_QUERY_DATA, f'{interface}.txt'), dtype=str, error_bad_lines=False)
# data[data == 'None'] = np.nan




db = BaseDB()
# # keys = db.queryData('ts_code,trade_date', interface)
# # keys = pd.DataFrame(keys, columns=['ts_code', 'trade_date'])
# # keys['in_db'] = 1
# # data = data.merge(keys, on=['ts_code', 'trade_date'], how='outer')
# # del keys
# # data = data[data['in_db'].isna()].drop(columns=['in_db']).reset_index(drop=True)
#
error = db.insert_multi_record(data, interface, nn=1000)
# # error = db.insert_multi_record(error, interface, nn=1)
# #
# # error['change_reason'] = error['change_reason'].apply(lambda x:x.replace('"', ''))
