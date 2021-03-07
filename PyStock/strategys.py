"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-02-03 15:43
IDE: PyCharm
Introduction:
"""
import backtrader as bt


class SimpleStrategy(bt.Strategy):
    params=(('maperiod', 15),
            ('printlog', True),)

    def __init__(self):
        #指定价格序列
        self.dataclose = self.datas[0].close

        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buyprice = None
        self.buycomm = None

        ##
        # self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)
        self.wma = bt.indicators.WeightedMovingAverage(self.datas[0], period=self.params.maperiod)


    #策略核心，根据条件执行买卖交易指令（必选）
    def next(self):
        # 记录收盘价
        #self.log(f'收盘价, {dataclose[0]}')
        if self.order: # 检查是否有指令等待执行,
            return
        # 检查是否持仓
        if not self.position: # 没有持仓
            #执行买入条件判断：收盘价格上涨突破15日均线
            if self.dataclose[0] > self.wma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                size = int(0.8 * self.broker.get_cash() / self.dataclose[0] / 100) * 100
                #执行买入
                self.order = self.buy(size=size)
        else:

            #执行卖出条件判断：收盘价格跌破15日均线
            if self.dataclose[0] < self.wma[0]  :
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                size = int(self.position.size * 1.0)
                #执行卖出
                self.order = self.sell(size=size)

    #交易记录日志（可省略，默认不输出结果）
    def log(self, txt, dt=None,doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')


    #记录交易执行情况（可省略，默认不输出结果）
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入: 价格:{order.executed.price}, 成本:{order.executed.value}, 手续费:{order.executed.comm}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出: 价格：{order.executed.price}, 成本: {order.executed.value}, 手续费{order.executed.comm}')
            self.bar_executed = len(self)

        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None


    #记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')


    #回测结束后输出结果（可省略，默认输出结果）
    def stop(self):
        self.log(f'期末总资金 {self.broker.getvalue()}', doprint=True)


class TrendBand(bt.Indicator):

    lines = ('lgb_pred', 'deepforest_pred')
    params = (('maperiod',1), ('maperiod',1))
    plotinfo = dict(subplot=True)

    def __init__(self):
        self.l.lgb_pred = self.data_lgb_pred
        self.l.deepforest_pred = self.data_deepforest_pred
        super(TrendBand, self).__init__()


class SimpleModelStrategy(bt.Strategy):
    params=(('maperiod', 12),
            ('printlog', True),)

    def __init__(self):
        #指定价格序列
        self.dataclose = self.datas[0].close

        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # self.sma = bt.indicators.SimpleMovingAverage(
        #               self.datas[0], period=self.params.maperiod)
        ##
        self.lgb_pred = self.datas[0].lgb_pred
        self.deepforest_pred = self.datas[0].deepforest_pred
        TrendBand(self.data)

    #策略核心，根据条件执行买卖交易指令（必选）
    def next(self):
        # 记录收盘价
        #self.log(f'收盘价, {dataclose[0]}')
        if self.order: # 检查是否有指令等待执行,
            return
        # 检查是否持仓

            #执行买入条件判断：收盘价格上涨突破15日均线
        if self.lgb_pred[0] >= 1:
            size = int(0.5 * self.broker.get_cash() / self.dataclose[0] / 100) * 100
            #执行买入
            self.order = self.buy(size=size)

        #执行卖出条件判断：收盘价格跌破15日均线
        elif self.lgb_pred[0] <= -1:
            size = int(self.position.size * 1.0 / 100) * 100
            #执行卖出
            self.order = self.sell(size=size)

    #交易记录日志（可省略，默认不输出结果）
    def log(self, txt, dt=None,doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    #记录交易执行情况（可省略，默认不输出结果）
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            # print(self.position)
            if order.isbuy():
                self.log(f'买入:价格:{order.executed.price},数量:{order.executed.size}手续费:{order.executed.comm}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:价格:{order.executed.price},数量:{order.executed.size}手续费:{order.executed.comm}')
            self.bar_executed = len(self)

        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

    #记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')

    def start(self):
        self.log(f'期初总资金 {self.broker.getvalue()}', doprint=True)

    #回测结束后输出结果（可省略，默认输出结果）
    def stop(self):
        self.log(f'期末总资金 {self.broker.getvalue()}', doprint=True)
