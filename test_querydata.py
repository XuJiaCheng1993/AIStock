"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-02-04 08:45
IDE: PyCharm
Introduction:
"""
import os
import datetime
import tushare as ts
import pandas as pd
import time
from tqdm import tqdm
from PyStock.configs import TS_TOKEN, PATH_QUERY_DATA
from PyStock.infos import info_interface
from PyStock.crawler import cycle_grasp_by_date


ts.set_token(TS_TOKEN)
interface = 'stock_basic'
field_date = 'trade_date'
field_duplicate = ['trade_date', 'ts_code']
table_id = 1



# data = cycle_grasp_by_date(interface, field_date, field_duplicate, table_id)


# ## 获取接口的头文件
head = info_interface(interface, table_id=table_id)['head']
data = ts.pro_api().query(interface, fileds=','.join(head.keys()), )
#
# # ## 循环抓取
# # pbar = tqdm(desc='collect')
# # data = pd.DataFrame()
# end_date = datetime.datetime.now().strftime('%Y%m%d')
# date_list = []
# # for _ in range(1000):
# #     index_basic = ts.pro_api().query(interface, fileds=','.join(head.keys()),
# #                                      start_date='19000101',
# #                                      end_date=end_date)
# #     data = pd.concat([data, index_basic], axis=0).reset_index(drop=True)
# #     date_list.append(index_basic[field_date].min())
# #     if len(index_basic) <= 0:
# #         break
# #     end_date = (pd.to_datetime(index_basic[field_date].min()) - datetime.timedelta(1)).strftime('%Y%m%d')
# #     time.sleep(0.1)
# #     pbar.update(1)
# # pbar.close()
# #
# # ## 交接口的日期重新查询，并去重
# # for dt in date_list:
# #     index_basic = ts.pro_api().query(interface, fileds=','.join(head.keys()), start_date=dt, end_date=dt)
# #     data = pd.concat([data, index_basic], axis=0).reset_index(drop=True)
# #     time.sleep(0.1)
# # data = data.drop_duplicates(subset=field_duplicate).reset_index(drop=True)
#
# ## 数据保存
data.to_csv(os.path.join(PATH_QUERY_DATA, f'{interface}.csv'), index=False)


