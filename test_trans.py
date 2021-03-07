#!/usr/bin/env python
# encoding: utf-8
'''
# @Time    : 2021/3/6 15:45
# @Author  : JiachengXu
# @Software: PyCharm
'''
import tushare as ts
from PyStock.configs import TS_TOKEN
from PyStock.transformers.trans import MomentumTransformer, OverlapTransformer

tf = OverlapTransformer()

ts_code = '000001.SZ'

## 获取数据
ts.set_token(TS_TOKEN)
df = ts.pro_api().query('daily', ts_code=ts_code)

df = df.sort_values(by='trade_date', ascending=True).reset_index(drop=True)
high, low, open, close, volume = df['high'], df['low'], df['open'], df['close'], df['vol']
# tf.params.timeperiod.default
tf.set_params({'timeperiod':{5, 10, 15, 20, 25, 30, 45, 60, 90}})

X = tf.transform(open=open, high=high, low=low, close=close, volume=volume)

# eval('high')

