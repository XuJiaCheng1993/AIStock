"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-02-19 13:44
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


js_formatter = """function (params) {
        console.log(params);
        return params.value;
    }"""


def split_data(origin_data) -> dict:
    # origin_data = origin_data[origin_data['trade_date'] >= '20080101'].reset_index(drop=True)
    # origin_data = origin_data[origin_data['trade_date'] <= '20190101'].reset_index(drop=True)
    data_copy = origin_data.drop_duplicates(subset=['month', ]).reset_index(drop=True)
    data_copy = origin_data[['trade_date', ]].merge(data_copy, how='left').drop(columns=['trade_date', 'month'])
    data_copy = data_copy.astype(float).interpolate()


    return {
        "datas": origin_data[['open', 'close', 'low', 'high']].astype(float).values.tolist(),
        "pct_chg":origin_data['close'].values.tolist(),
        "times": origin_data['trade_date'].values.tolist(),
        "pe": origin_data['pe'].astype(float).values.tolist(),
        "m2_yoy":data_copy['m2_yoy'].astype(float).values.tolist(),
        "m2_mom": data_copy['m2_mom'].astype(float).values.tolist(),
        "m2": data_copy['m2_y'].astype(float).values.tolist(),
        # "shibor_on":origin_data['on'].astype(float).values.tolist(),
        "shibor_1y": origin_data['1y'].astype(float).values.tolist(),
        "us_10y": origin_data['y10'].astype(float).values.tolist(),
        "cpi_nt_yoy": data_copy['nt_yoy'].astype(float).values.tolist(),
        # "cpi_town_yoy": origin_data['town_yoy'].astype(float).values.tolist(),
        # "cpi_cnt_yoy": origin_data['cnt_yoy'].astype(float).values.tolist(),
        "ppi_yoy":data_copy['ppi_yoy'].astype(float).values.tolist(),

    }

ehcarts_data = pd.read_csv('data.csv', dtype=str)
data = split_data(origin_data=ehcarts_data)


colors = ["SteelBlue", "SeaGreen", "Chocolate", "FireBrick"]


line = (
    Line(init_opts=opts.InitOpts(width="1760px", height="800px"))
    .add_xaxis(xaxis_data=data['times'])
        .add_yaxis(series_name="沪深300",
                   y_axis=data['pct_chg'],
                   yaxis_index=0,
                   linestyle_opts = opts.LineStyleOpts(width=3),
                   # color="SteelBlue",
                   )
        .add_yaxis(series_name="SHIBOR",
                   y_axis=data['shibor_1y'],
                   yaxis_index=1,
linestyle_opts = opts.LineStyleOpts(width=2),
                   # color="SteelBlue",
                   )

        .add_yaxis(series_name="美债10Y",
                   y_axis=data['us_10y'],
                   yaxis_index=1,
linestyle_opts = opts.LineStyleOpts(width=2),
                   # color="SteelBlue",
                   )
        # .add_yaxis(series_name="pe",
        #            y_axis=data['pe'],
        #            yaxis_index=2,
        #            linestyle_opts = opts.LineStyleOpts(width=3)
        #            # color="SeaGreen"
        #            )



        .add_yaxis(series_name="cpi",
                   y_axis=data['cpi_nt_yoy'],
                   linestyle_opts = opts.LineStyleOpts(width=2),
                   yaxis_index=1,
                   # color="FireBrick"
                   )
        .add_yaxis(series_name="ppi",
                   y_axis=data['ppi_yoy'],
                   linestyle_opts = opts.LineStyleOpts(width=2),
                   yaxis_index=1,
                   # color="FireBrick"
                   )

        .add_yaxis(series_name="m2_rate",
                   y_axis=data['m2_mom'],
                   linestyle_opts=opts.LineStyleOpts(width=2, curve=100),
                   yaxis_index=1,
                   # color="FireBrick"
                   )

        .add_yaxis(series_name="m2",
                   y_axis=data['m2'],
                   linestyle_opts=opts.LineStyleOpts(width=3),
                   yaxis_index=2,
                   # color="FireBrick"
                   )

    # .extend_axis(
    #     yaxis=opts.AxisOpts(
    #         name="净值",
    #         type_="value",
    #         position="left",
    #         axisline_opts=opts.AxisLineOpts(
    #             linestyle_opts=opts.LineStyleOpts(color="SteelBlue")
    #         ),
    #         axislabel_opts=opts.LabelOpts(formatter="{value} %"),
    #
    #     )
    # )

    # .extend_axis(
    #     yaxis=opts.AxisOpts(
    #         name="货币",
    #         type_="value",
    #         position="right",
    #
    #         # axisline_opts=opts.AxisLineOpts(
    #         #     linestyle_opts=opts.LineStyleOpts(color="SteelBlue")
    #         # ),
    #         axislabel_opts=opts.LabelOpts(formatter="{value} %"),
    #
    #     )
    # )

    .extend_axis(
        yaxis=opts.AxisOpts(
            name="百分比",
            type_="value",
            position="right",
            offset=0,

            # axisline_opts=opts.AxisLineOpts(
            #     linestyle_opts=opts.LineStyleOpts(color="SeaGreen")
            # ),
            axislabel_opts=opts.LabelOpts(formatter="{value} %"),

        )
    )

        .extend_axis(
        yaxis=opts.AxisOpts(
            name="RMB",
            type_="value",
            position="right",
            offset=60,

            # axisline_opts=opts.AxisLineOpts(
            #     linestyle_opts=opts.LineStyleOpts(color="SeaGreen")
            # ),
            axislabel_opts=opts.LabelOpts(formatter="{value} 亿元"),

        )
    )


    .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    .set_global_opts(
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        datazoom_opts=[opts.DataZoomOpts(type_="inside"), opts.DataZoomOpts()],

    )
)


kline = (
    Kline()
    .add_xaxis(xaxis_data=data["times"])
    .add_yaxis(series_name="沪深300",
                   y_axis=data["datas"],
                   itemstyle_opts=opts.ItemStyleOpts(color="#ef232a", color0="#14b143",
                                                     border_color="#ef232a", border_color0="#14b143", ),
               yaxis_index=0,)
)



line.render('hs300.html')