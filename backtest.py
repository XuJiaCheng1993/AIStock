"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-02-01 13:20
IDE: PyCharm
Introduction:
"""
import tushare as ts
from PyStock.configs import TS_TOKEN
import pandas as pd
import numpy as np

ts.set_token(TS_TOKEN)

class MyStrategy():
    def __init__(self, stock_info):
        self.stock_info = stock_info

    def sell_strategy(self):
        sell = {}
        if self.stock_info.loc['601128.SH', 'lgb_pred'] == -2:
            sell = {'601128.SH':0.9}
        if self.stock_info.loc['601128.SH', 'lgb_pred'] == -1:
            sell = {'601128.SH':0.5}
        return sell

    def buy_strategy(self):
        buy = {}
        if self.stock_info.loc['601128.SH', 'lgb_pred'] == 2:
            buy = {'601128.SH':0.9}
        if self.stock_info.loc['601128.SH', 'lgb_pred'] == 1:
            buy = {'601128.SH':0.7}
        return buy

    def run(self):
        return dict(sell=self.sell_strategy(), buy=self.buy_strategy())



class BackTest():
    def __init__(self, asserts=10000, commission=0.00025):
        self.init_asserts = asserts
        hist = pd.read_csv('test.csv')
        hist['trade_date'] = hist['trade_date'].astype(int).astype(str)
        self.hist = hist
        self.commission = commission
        # self.now = now
        self.hold = {'cash':asserts,
                     'stock':{},
                     }


    def buy(self, code, price, shares):
        ''' 买入
        code: str 股票代码
        price: float or None 最高可买入的价格, 如果为None则按市价买入
        shares: int 买入股票手数
        '''
        assert self.hold['cash'] >= price * shares

        if code in self.hold['stock'].keys():
            hold_code = self.hold['stock'][code]
            hold_code['price'] = (hold_code['price'] * hold_code['shares'] + price * shares ) / (hold_code['shares'] + shares)
            hold_code['shares'] = hold_code['shares'] + shares
        else:
            hold_code = dict(price=price, shares=shares)

        self.hold['stock'][code] = hold_code


        ## 计算手续费
        cost = min(price * shares * 100 * self.commission, 5)
        self.hold['cash'] -= (price * shares * 100 + cost)


        return self


    def sell(self, code, price, shares):
        ''' 卖出'''
        assert code in self.hold['stock'].keys()
        assert shares <= self.hold['stock'][code]['shares']
        self.hold['stock'][code]['shares'] -= shares
        cost = min(price * shares * 100 * self.commission, 5)
        self.hold['cash'] += (price * shares * 100 - cost)
        return self

    def run(self, start_date, end_date):
        ''' 运行'''
        trade_date = ts.pro_api().query('trade_cal', start_date=start_date, end_date=end_date, is_open='1')['cal_date'].tolist()

        indicator = pd.DataFrame(index=trade_date, columns=['cash', 'stock', 'asserts'])
        for td in trade_date:
            stock_info = self.hist[self.hist['trade_date'] == td].set_index('ts_code')
            operate = MyStrategy(stock_info).run()

            if operate['sell']:
                for code, radio in operate['sell'].items():
                    if code in self.hold['stock'].keys() and self.hold['stock'][code]['shares'] > 0:
                        price = stock_info.loc[code, 'close']
                        shares = int(self.hold['stock'][code]['shares'] * radio)
                        if shares > 0:
                            self.sell(code, price, shares)
                            print(f'{td} sell {code} {shares} {price}')

            if operate['buy']:
                for code, radio in operate['buy'].items():
                    price = stock_info.loc[code, 'close']
                    shares = np.floor(self.hold['cash'] * radio / price / 100)
                    if shares > 0:
                        self.buy(code, price, shares)
                        print(f'{td} buy {code} {shares}  {price}')


            stock_val = sum([stock_info.loc[k, 'close'] * v['shares'] * 100  for k, v in self.hold['stock'].items() if k])
            indicator.loc[td, :] = self.hold['cash'], stock_val, self.hold['cash'] + stock_val

        indicator['profit'] = ((indicator['asserts'] - self.init_asserts) / self.init_asserts).apply(lambda x:f'{x:.2%}')
        self.indicator = indicator
        return self




a = BackTest()
a.run('20200101', '20210131')














