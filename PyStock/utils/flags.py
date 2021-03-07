#!/usr/bin/env python
# encoding: utf-8
'''
# @Time    : 2021/1/26 21:46
# @Author  : JiachengXu
# @Software: PyCharm
'''
import os

def check_flag_file(path, flag_type='.ok'):
    ''' 检查路径中是否有 ok 文件, 若有则返回最新ok文件的日期'''
    date_ok = None
    file_lists = os.listdir(path)
    if len(file_lists) > 0:
        file_ok = [f for f in file_lists if f.find(flag_type) >= 0]
        if len(file_ok) > 0:
            date_ok = file_ok[0].replace(flag_type, '')
    return date_ok


def generate_flag_file(event='ok', fail_file_old=None, fail_file_new=None, ok_file_old=None, ok_file_new=None):
    ''' 生成处理标志'''
    assert event in ['ok', 'fail']

    if event == 'ok':
        ## 删除fail标志
        if os.path.exists(fail_file_old):
            os.remove(fail_file_old)

        ## 写入ok标志
        if os.path.exists(ok_file_old):
            os.rename(ok_file_old, ok_file_new)
        else:
            with open(ok_file_new, 'w') as file:
                file.write('')
    else:
        with open(fail_file_new, 'w') as file:
            file.write('')