#!/usr/bin/env python
# encoding: utf-8
'''
# @Time    : 2021/1/26 21:54
# @Author  : JiachengXu
# @Software: PyCharm
'''
import os
import datetime
from dateutil.parser import parse
from .utils import check_flag_file, generate_flag_file
from .configs import logger, PATH_QUERY_DATA
from .crawler import multiThreadQuery


def runGeneralQuery(interface='daily'):
    ''' '''
    ## 运行开始日期
    date_last = check_flag_file(PATH_QUERY_DATA, flag_type=f'.{interface}.ok')
    flag_name = dict(fail_file_old=os.path.join(PATH_QUERY_DATA, f'{date_last}.{interface}.fail'),
                     ok_file_old=os.path.join(PATH_QUERY_DATA, f'{date_last}.{interface}.ok'))
    date_last = (parse(date_last) + datetime.timedelta(1)).strftime('%Y%m%d') if date_last is not None else date_last

    ## 运行结束日期
    date_cur = datetime.datetime.now()
    date_cur = (date_cur if date_cur.hour >= 19 else date_cur - datetime.timedelta(1)).strftime('%Y%m%d')
    flag_name = dict(fail_file_new=os.path.join(PATH_QUERY_DATA, f'{date_cur}.{interface}.fail'),
                     ok_file_new=os.path.join(PATH_QUERY_DATA, f'{date_cur}.{interface}.ok'),
                     **flag_name)

    ## 判断是否需要运行
    gen_query = multiThreadQuery(interface=interface, start_date=date_last, end_date=date_cur)
    if not gen_query.query_flag:
        logger.info(f'[{gen_query.interface_name}] StartDate={date_last} EndDate={date_cur}. No new data need update!')
        return gen_query

    logger.info(f'[{gen_query.interface_name}] StartDate={date_last} EndDate={date_cur}. Begin to run!')
    ## 开始运行
    gen_query.run()

    ## 生成标志文件
    unget_date = [k for k, v in gen_query.query_flag.items() if not v]
    if not unget_date:
        generate_flag_file(event='ok', **flag_name)
        logger.info(f'[{gen_query.interface_name}] StartDate={date_last} EndDate={date_cur}. Run complete!')
    else:
        generate_flag_file(event='fail', **flag_name)
        logger.warning(f'[{gen_query.interface_name}] Date {",".join(unget_date)} are not update!')
    return gen_query

