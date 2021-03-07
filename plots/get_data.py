"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-02-18 08:48
IDE: PyCharm
Introduction:
"""


from PyStock.crawler import cycle_grasp_by_date
from PyStock.configs import TS_TOKEN
import tushare as ts
import pandas as pd


ts.set_token(TS_TOKEN)


index = cycle_grasp_by_date(interface='index_daily', field_date='trade_date', query_kwargs=dict(ts_code='000300.SH') )
daily = cycle_grasp_by_date(interface='index_dailybasic', field_date='trade_date', query_kwargs=dict(ts_code='000300.SH') )
shibor = cycle_grasp_by_date(interface='shibor', field_date='date', field_duplicate = ['date', ], )
us_tycr = cycle_grasp_by_date(interface='us_tycr', field_date='date', field_duplicate = ['date', ], )
cn_cpi = ts.pro_api().query('cn_cpi')
cn_ppi = ts.pro_api().query('cn_ppi')
cn_m = ts.pro_api().query('cn_m')



data = pd.merge(index, daily, on=['ts_code', 'trade_date'], how='left').drop(columns=['ts_code'])
rate = shibor.merge(us_tycr, on='date', how='outer', suffixes=('_shibor', '_ustycr'))
data = data.merge(rate, left_on='trade_date', right_on='date', how='left').drop(columns=['date'])


data['month'] = data['trade_date'].apply(lambda x:x[:6])
data = data.merge(cn_cpi, how='left', on='month')
data = data.merge(cn_ppi, how='left', on='month')
data = data.merge(cn_m, how='left', on='month')

data = data.sort_values(by='trade_date').reset_index(drop=True)


data.to_csv('data.csv', index=False)
