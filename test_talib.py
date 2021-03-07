"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-03-04 15:31
IDE: PyCharm
Introduction:
"""

import tushare as ts
import numpy as np
import pandas as pd
from PyStock.configs import TS_TOKEN
import talib


ts_code = '000001.SZ'

## 获取数据
ts.set_token(TS_TOKEN)
df = ts.pro_api().query('daily', ts_code=ts_code)

df = df.sort_values(by='trade_date', ascending=True).reset_index(drop=True)
high, low, open, close, volume = df['high'], df['low'], df['open'], df['close'], df['vol']

a = talib.CDL3INSIDE(open, high, low, close)