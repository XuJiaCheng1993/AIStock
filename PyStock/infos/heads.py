"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-01-26 10:38
IDE: PyCharm
Introduction: TuShare接口返回字段并相关中文释义
"""

import os
import json
import pandas as pd

__infos = pd.read_excel(os.path.join(os.path.dirname(__file__), 'headcache',  'interfaces.xlsx'), dtype=str)

STOCK_API_LIST = __infos[__infos['接口权属'] == 'stock']['接口名称'].tolist()
INDEX_API_LIST = __infos[__infos['接口权属'] == 'index']['接口名称'].tolist()
FUND_API_LIST = __infos[__infos['接口权属'] == 'fund']['接口名称'].tolist()
FUT_API_LIST = __infos[__infos['接口权属'] == 'fut']['接口名称'].tolist()
OPT_API_LIST = __infos[__infos['接口权属'] == 'opt']['接口名称'].tolist()
CB_API_LIST = __infos[__infos['接口权属'] == 'cb']['接口名称'].tolist()
FX_API_LIST = __infos[__infos['接口权属'] == 'fx']['接口名称'].tolist()
HK_API_LIST = __infos[__infos['接口权属'] == 'hk']['接口名称'].tolist()


def load_or_dump_json(filename, dump_file=None):
    if dump_file is None:
        with open(os.path.join(os.path.dirname(__file__), 'headcache', f'head_{filename}.json'), 'r') as file:
            head = json.load(file)
        return head
    else:
        with open(os.path.join(os.path.dirname(__file__), 'headcache',  f'head_{filename}.json'), 'w') as file:
            json.dump(dump_file, file, ensure_ascii=False)


def info_interface(interface, table_id=1):
    infos = __infos[__infos['接口名称'] == interface].reset_index(drop=True)

    try:
        head = load_or_dump_json(interface)
    except:
        html = pd.read_html(f'https://waditu.com/document/2?doc_id={infos["网页ID"].values[0]}')[table_id]
        head = {k:v for k, v in zip(html['名称'], html['描述'])}
        load_or_dump_json(interface, head)


    infos = dict(head=head,
                score_require=infos['积分要求'].astype(int).values[0],
                records_per_query=infos['每次限制条数'].astype(int).values[0],
                name=infos["接口描述"].values[0])
    return infos



