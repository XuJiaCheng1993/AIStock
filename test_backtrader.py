"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-02-03 08:28
IDE: PyCharm
Introduction:
"""


import pandas as pd
import matplotlib.pyplot as plt
import backtrader as bt
from PyStock.strategys import SimpleModelStrategy, SimpleStrategy




class MyPandasData(bt.feeds.PandasData):
    lines = ('lgb_pred', 'vol', 'deepforest_pred')
    params = (('lgb_pred', -1), ('vol', -1), ('deepforest_pred', -1), )

#获取数据
df = pd.read_csv('test.csv').rename(columns={'vol':'volume'})
df = df[df['trade_date'] >= 20200101]
df.sort_values(by='trade_date', inplace=True)
df['trade_date'] = pd.to_datetime(df['trade_date'].astype(int).astype(str))
df.set_index('trade_date', inplace=True)


### 回测
#创建回测主控制器
cerebro = bt.Cerebro()
cerebro.addstrategy(SimpleModelStrategy)
#将数据加载至回测系统
data = MyPandasData(dataname=df)
cerebro.adddata(data)
#broker设置资金、手续费
cerebro.broker.setcash(10000)
cerebro.broker.setcommission(commission=0.00025)
#设置买入设置，策略，数量
cerebro.addsizer(bt.sizers.FixedSize)
# cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
results =  cerebro.run()

## 画图
plt.figure()
[fig, ] = cerebro.plot(style='candlestick', width=18, height=12, dpi=2000, iplot=False, numfigs=1)
plt.show(fig)



