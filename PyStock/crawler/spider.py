"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-01-22 15:20
IDE: PyCharm
Introduction:
"""

import os
import datetime
import tushare as ts
import pandas as pd
import time
from tqdm import tqdm
import threadpool
import threading
import random
from ..configs import *
from ..infos import info_interface, FUND_API_LIST, STOCK_API_LIST, INDEX_API_LIST


ts.set_token(TS_TOKEN)


class baseQuery(object):
    def __init__(self, interface, *args, **kwargs):
        ''' 初始化类'''
        self.__interface = interface

        info = info_interface(interface)
        score_require = 0 if info['score_require'] is None else info['score_require']
        if TS_SCORE < score_require:
            raise Exception('账户积分不足，无权限查询该接口')

        self.ts_pro = ts.pro_api()

        self.__interface = interface
        self.__head = info['head']
        self.__interface_name = info['name']



    @property
    def interface(self):
        return self.__interface

    @property
    def interface_name(self):
        return self.__interface_name

    @property
    def head(self):
        return self.__head



class onceQuery(baseQuery):
    def query(self, *args, **kwargs):
        return self.ts_pro.query(api_name=self.interface, fields=','.join(self.head.keys()), *args, **kwargs)


    def save_to_txt(self, query):
        ''' 将查询结果存入本地txt文件 '''
        ## 数据保存
        with open(os.path.join(PATH_QUERY_DATA, f'{self.interface}.txt'), 'a+', encoding='utf-8-sig') as dump_file:
            query = '\n'.join([','.join(val) for val in query.astype(str).values])
            dump_file.write(query + '\n')


    def run(self, retry=5, *args, **kwargs):
        ''' 运行'''
        ## 查询数据，直到查到数据 或者达到查询上限未知
        for _ in range(retry):
            query = self.query(*args, **kwargs)
            if len(query) > 0:
                self.save_to_txt(query)
                break
        return self



class multiThreadQuery(baseQuery):
    ''' 多线程查询Tushare Pro 数据'''
    def __init__(self, target_field='trade_date', query_list=None,  start_date=None, end_date=None, *args, **kwargs):
        super(multiThreadQuery, self).__init__(*args, **kwargs)
        ''' 初始化类'''
        self.__target_field = target_field
        self.mutex = threading.Lock()  # 创建线程锁

        if query_list is None:
            self.__get_query_list(start_date=start_date, end_date=end_date)
        else:
            self.__query_flag = query_list


    def __get_query_list(self, *args, **kwargs):
        ''' 获取查询列表'''
        if 'date' in self.__target_field:
            query_list = self.__get_date_list(*args, **kwargs)
        elif 'code' in self.__target_field:
            query_list = self.__get_stock_list(*args, **kwargs)
        elif 'id' in self.__target_field:
            query_list = [f'TS{f}' for f in range(880)]
        else:
            query_list = []

        self.__query_flag = {f: False for f in query_list}
        return self


    def __get_stock_list(self, *args, **kwargs):
        ''' 获取TS代码列表'''
        assert self.interface in STOCK_API_LIST + FUND_API_LIST + INDEX_API_LIST
        code_field= 'ts_code'
        if self.interface in STOCK_API_LIST:
            api_name = 'stock_basic'
        elif self.interface in FUND_API_LIST:
            api_name = 'fund_basic'
        elif self.interface in ['index_member', ]:
            api_name = 'index_classify'
            code_field = 'index_code'
        else:
            api_name = 'index_basic'
        stock_list = self.ts_pro.query(api_name)[code_field].tolist()



        return stock_list



    def __get_date_list(self, start_date=None, end_date=None, *args, **kwargs):
        ''' 获取开始日期到结束之间的所有交易日列表'''
        if start_date is None:
            start_date = '19900101'

        if end_date is None:
            end_date = datetime.datetime.now().strftime('%Y%m%d')

        trade_date_list = self.ts_pro.trade_cal(exchange='SSE',
                                                is_open='1',
                                                start_date=start_date,
                                                end_date=end_date,
                                                fields='cal_date',
                                                *args, **kwargs)['cal_date'].tolist()
        return trade_date_list



    def __get_once(self, query):
        ''' 获取每个交易日的所有股票行情数据'''
        ## 查询函数参数
        kwargs = {'api_name':self.interface,
                  f'{self.__target_field}':query,
                  'fields':','.join(self.head.keys())}

        ## 查询
        for _ in range(RETRY_TIMES):
            try:
                once_query = self.ts_pro.query(**kwargs)
                time.sleep(0.25 + 0.75 * random.random() )
                break
            except:
                time.sleep(1.0)
        else:
            once_query = pd.DataFrame()
        return once_query


    def __save_to_txt(self, query):
        ''' 将获取的数据保存到txt文件'''
        ## 获取每日沪深股行情数据
        once_query = self.__get_once(query)
        nums = once_query.shape[0]

        ## 存入txt
        if nums > 0:
            ## dataframe 转换成 txt 文本形式
            once_query = '\n'.join([','.join(val) for val in once_query.astype(str).values])

            ## 写入文本
            self.mutex.acquire()
            self.dump_file.write(once_query + '\n')
            self.num_of_url_records += nums
            self.__query_flag.update({query:True})
            self.pbar.update(1)
            self.mutex.release()


    def run_multithread(self, query_list):
        ''' 多线程运行查询网页信息'''
        self.pbar = tqdm(total=len(query_list), desc='Collect Data')
        self.num_of_url_records = 0
        with open(os.path.join(PATH_QUERY_DATA, f'{self.interface}.txt'), 'a+', encoding='utf-8-sig') as self.dump_file:
            arg = zip(zip(query_list), [None, ] * len(query_list))
            pool = threadpool.ThreadPool(THREAD_NUMS )
            my_requests = threadpool.makeRequests(self.__save_to_txt, arg)
            [pool.putRequest(req) for req in my_requests]
            pool.wait()
            pool.dismissWorkers(THREAD_NUMS , do_join=True)  # 完成后退出
        self.pbar.close()


    def run(self, retry=5):
        ''' 运行'''
        ## 将漏查询的继续查询，直到全部查询完毕or达到查询次数上限
        for _ in range(retry):
            query_list = [k for k, v in self.query_flag.items() if not v]
            if query_list:
                self.run_multithread(query_list)
            else:
                break
        return self


    @property
    def query_flag(self):
        return self.__query_flag


def cycle_grasp_by_date(interface='moneyflow_hsgt', field_date='trade_date', field_duplicate = ['trade_date', ],
                        table_id=1, query_kwargs={}):
    ''' 一次无法抓全数据时，根据开始结束日期循环抓取'''
    ## 获取接口的头文件
    head = info_interface(interface, table_id=table_id)['head']

    ## 循环抓取
    pbar = tqdm(desc='collect')
    data = pd.DataFrame()
    end_date = datetime.datetime.now().strftime('%Y%m%d')
    date_list = []
    for _ in range(1000):
        index_basic = ts.pro_api().query(interface, fileds=','.join(head.keys()), start_date='19000101',
                                         end_date=end_date, **query_kwargs)
        data = pd.concat([data, index_basic], axis=0).reset_index(drop=True)
        date_list.append(index_basic[field_date].min())
        if len(index_basic) <= 0:
            break
        end_date = (pd.to_datetime(index_basic[field_date].min()) - datetime.timedelta(1)).strftime('%Y%m%d')
        time.sleep(0.1)
        pbar.update(1)
    pbar.close()

    ## 交接口的日期重新查询，并去重
    for dt in date_list:
        index_basic = ts.pro_api().query(interface, fileds=','.join(head.keys()), start_date=dt, end_date=dt, **query_kwargs)
        data = pd.concat([data, index_basic], axis=0).reset_index(drop=True)
        time.sleep(0.1)
    data = data.drop_duplicates(subset=field_duplicate).reset_index(drop=True)

    ## 数据保存
    data.to_csv(os.path.join(PATH_QUERY_DATA, f'{interface}.csv'), index=False)
    return data


