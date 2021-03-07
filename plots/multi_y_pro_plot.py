"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-02-20 13:47
IDE: PyCharm
Introduction:
"""


import numpy as np
import pandas as pd
from typing import List, Sequence, Union

from pyecharts.options import MarkLineItem, MarkLineOpts
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Kline, Line, Bar, Grid

def split_data(origin_data) -> dict:
    return {
        "times": origin_data['trade_date'].values.tolist(),
        'close':origin_data['close'].astype(float).values.tolist(),
        "total_mv": origin_data['total_mv'].astype(float).values.tolist(),
        "float_mv": origin_data['float_mv'].astype(float).values.tolist(),
        "total_share": origin_data['total_share'].astype(float).values.tolist(),
        "float_share": origin_data['float_share'].astype(float).values.tolist(),
        "free_share": origin_data['free_share'].astype(float).values.tolist(),
        "turnover_rate": origin_data['turnover_rate'].astype(float).values.tolist(),
        "turnover_rate_f": origin_data['turnover_rate_f'].astype(float).values.tolist(),
        "pe": origin_data['pe'].astype(float).values.tolist(),
        "pe_ttm": origin_data['pe_ttm'].astype(float).values.tolist(),
        "pb": origin_data['pb'].astype(float).values.tolist(),
        "shibor1y":origin_data['1y'].astype(float).values.tolist(),
    }

ehcarts_data = pd.read_csv('data.csv', dtype=str)
data = split_data(origin_data=ehcarts_data)

bar = (
        Bar(init_opts=opts.InitOpts(width="1760px", height="800px"))
        .add_xaxis(xaxis_data=data['times'])
        .add_yaxis(series_name="总市值",
                   yaxis_data=data['total_mv'],
                   yaxis_index=0,
                   itemstyle_opts = opts.ItemStyleOpts(opacity=0.3)

                       # color="SteelBlue",
                       )
        .add_yaxis(series_name="流通市值",
                   yaxis_data=data['float_mv'],
                   yaxis_index=0,
                   itemstyle_opts = opts.ItemStyleOpts(opacity=0.3)
                       # color="SteelBlue",
                       )

        .add_yaxis(series_name="总股本",
                   yaxis_data=data['total_share'],
                   yaxis_index=1,
                   itemstyle_opts = opts.ItemStyleOpts(opacity=0.3)
                   # color="SteelBlue",
                   )
        .add_yaxis(series_name="流通股本",
                   yaxis_data=data['float_share'],
                   yaxis_index=1,
                   itemstyle_opts = opts.ItemStyleOpts(opacity=0.3)
                   # color="SteelBlue",
                   )

        .add_yaxis(series_name="自由股本",
                   yaxis_data=data['free_share'],
                   yaxis_index=1,
                   itemstyle_opts = opts.ItemStyleOpts(opacity=0.3)
                   # color="SteelBlue",
                   )



        .extend_axis(
            yaxis=opts.AxisOpts(
                name="市值",
                type_="value",
                position="right",
                offset=0,
                # max_ = 20 * np.nanmax(data['total_mv']),
                # min_ = 0.8 * np.nanmin(data['float_mv']),

                # axisline_opts=opts.AxisLineOpts(
                #     linestyle_opts=opts.LineStyleOpts(color="SeaGreen")
                # ),
                axislabel_opts=opts.LabelOpts(formatter="{value} 元"),

            )
        )

        .extend_axis(
            yaxis=opts.AxisOpts(
                name="百分比",
                type_="value",
                position="left",
                offset=0,
                # min_=-15,
                # max_=30,

                # axisline_opts=opts.AxisLineOpts(
                #     linestyle_opts=opts.LineStyleOpts(color="SeaGreen")
                # ),
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),

            )
        )
            .extend_axis(
            yaxis=opts.AxisOpts(
                name="净值",
                type_="value",
                position="right",
                offset=100,
                max_=1.4 * max(data['close']),
                min_=0.4 * min(data['close']),

                # axisline_opts=opts.AxisLineOpts(
                #     linestyle_opts=opts.LineStyleOpts(color="SeaGreen")
                # ),
                axislabel_opts=opts.LabelOpts(formatter="{value}"),

            )
        )


        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
                yaxis_opts=opts.AxisOpts(
                name="股本",
                type_="value",
                position="right",
                offset=80,
                # max_ = 1.5 * np.nanmax(data['total_share']),
                # min_=  0.8 * np.nanmin(data['free_share']),
                # axisline_opts=opts.AxisLineOpts(
                #     linestyle_opts=opts.LineStyleOpts(color="SeaGreen")
                # ),
                axislabel_opts=opts.LabelOpts(formatter="{value} 股"),

            ),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        datazoom_opts=[opts.DataZoomOpts(type_="inside"), opts.DataZoomOpts()],

    )
)


line = (
        Line()
        .add_xaxis(xaxis_data=data['times'])
        .add_yaxis(series_name="换手率",
                   y_axis=data['turnover_rate'],
                   yaxis_index=2,
                   linestyle_opts = opts.LineStyleOpts(width=3),)
        .add_yaxis(series_name="流通股换手率",
                   y_axis=data['turnover_rate_f'],
                   yaxis_index=2,
                   linestyle_opts=opts.LineStyleOpts(width=3), )

        .add_yaxis(series_name="市盈率",
                   y_axis=data['pe'],
                   yaxis_index=2,
                   linestyle_opts=opts.LineStyleOpts(width=3), )

        .add_yaxis(series_name="市盈率TTM",
                   y_axis=data['pe_ttm'],
                   yaxis_index=2,
                   linestyle_opts=opts.LineStyleOpts(width=3), )

        .add_yaxis(series_name="市净率",
                   y_axis=data['pb'],
                   yaxis_index=2,
                   linestyle_opts=opts.LineStyleOpts(width=3), )

        .add_yaxis(series_name="SHIBOR1Y",
                   y_axis=data['shibor1y'],
                   yaxis_index=2,
                   linestyle_opts=opts.LineStyleOpts(width=3), )

        .add_yaxis(series_name="沪深300",
                   y_axis=data['close'],
                   yaxis_index=3,
                   linestyle_opts=opts.LineStyleOpts(width=5),
                       )



.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
)


bar.overlap(line).render('hs300_type2.html')