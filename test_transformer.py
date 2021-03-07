"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-01-29 14:03
IDE: PyCharm
Introduction:
"""
import tushare as ts
import numpy as np
import pandas as pd
from PyStock.transformers.trans import OverlapTransformer, MomentumTransformer
from PyStock.configs import TS_TOKEN
import lightgbm as lgb
from deepforest import CascadeForestClassifier


ts_code = '000001.SZ'

## 获取数据
ts.set_token(TS_TOKEN)
df = ts.pro_api().query('daily', ts_code=ts_code)
basic = ts.pro_api().query('daily_basic', ts_code=ts_code)
moneyflow = ts.pro_api().query('moneyflow', ts_code=ts_code)
basic = basic.merge(moneyflow, how='left', on=['ts_code', 'trade_date']).fillna(0.)
basic_cols = [f for f in basic.columns if f not in ['ts_code', 'trade_date']]
df = df.sort_values(by='trade_date').reset_index(drop=True)
basic = basic.sort_values(by='trade_date').reset_index(drop=True)


## 计算 OverlapStudies 指标
high, low, open, close, volume = df['high'], df['low'], df['open'], df['close'], df['vol']
feature1 = OverlapTransformer().set_params({'timeperiod':{10, 20, 30}}).transform(high=high, low=low, close=close)
feature2 = MomentumTransformer().set_params({'timeperiod':{10, 20, 30}}).transform(open=open, high=high, low=low, close=close, volume=volume)
feature = pd.concat([feature1, feature2], axis=1)

# feature = pd.concat([feature, basic[basic_cols]], axis=1)
cols = [f for f in feature.columns]


## 根据收益率计算y值
profit = df[['trade_date', 'close']].copy()
close = profit['close'].values.reshape(-1)
for i in range(1, 11):
    profit[f'd{i}fit'] = (np.hstack((close[i:], np.zeros([i]))) - close) / close
    feature[f'd{i}fit'] = pd.cut(profit[f'd{i}fit'], bins=[-0.9,  -0.03, 0.03, 0.9], labels=[-1, 0, 1])


## 训练简单模型
test = feature[feature['d10fit'].isna()].reset_index(drop=True)
X_tr = feature.iloc[:-400, :]
X_val = feature.iloc[-400:-10, :]

model = CascadeForestClassifier()
model.fit(X_tr[cols].values, X_tr[f'd5fit'].values)
lgb = lgb.LGBMClassifier(n_estimators=1000)
lgb.fit(X_tr[cols], X_tr[f'd5fit'])
p_val = model.predict(feature[cols].values)
df['deepforest_pred'] = model.predict(feature[cols].values)
df['lgb_pred'] = lgb.predict(feature[cols])
df['real_profit'] = profit['d5fit']

## 数据保存
df.to_csv('test.csv', index=False)


