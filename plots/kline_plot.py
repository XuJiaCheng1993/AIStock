"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-02-18 13:39
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
    origin_data = origin_data[origin_data['trade_date'] >= '20080101'].reset_index(drop=True)
    # origin_data = origin_data[origin_data['trade_date'] <= '20190101'].reset_index(drop=True)

    return {
        "datas": origin_data[['open', 'close', 'low', 'high']].astype(float).values.tolist(),
        "times": origin_data['trade_date'].values.tolist(),
        "pe": origin_data['pe'].astype(float).values.tolist(),
        "m0_yoy":origin_data['m0_yoy'].astype(float).values.tolist(),
        "m1_yoy":origin_data['m1_yoy'].astype(float).values.tolist(),
        "m2_yoy":origin_data['m2_yoy'].astype(float).values.tolist(),
        "shibor_on":origin_data['on'].astype(float).values.tolist(),
        "shibor_1y": origin_data['1y'].astype(float).values.tolist(),
        "cpi_nt_yoy": origin_data['nt_yoy'].astype(float).values.tolist(),
        "cpi_town_yoy": origin_data['town_yoy'].astype(float).values.tolist(),
        "cpi_cnt_yoy": origin_data['cnt_yoy'].astype(float).values.tolist(),
        "ppi_yoy":origin_data['ppi_yoy'].astype(float).values.tolist(),
    }




def calculate_ma(day_count: int):
    result: List[Union[float, str]] = []

    for i in range(len(data["times"])):
        if i < day_count:
            result.append("-")
            continue
        sum_total = 0.0
        for j in range(day_count):
            sum_total += float(data["datas"][i - j][1])
        result.append(abs(float("%.2f" % (sum_total / day_count))))
    return result


def draw_chart():
    ## K线
    kline = (
        Kline()
        .add_xaxis(xaxis_data=data["times"])
        .add_yaxis(series_name="",
                   y_axis=data["datas"],
                   itemstyle_opts=opts.ItemStyleOpts(color="#ef232a", color0="#14b143",
                                                     border_color="#ef232a", border_color0="#14b143",), )


        .set_global_opts(
            title_opts=opts.TitleOpts(title="周期图表", pos_top="0"),
            xaxis_opts=opts.AxisOpts(type_="category", is_scale=True, boundary_gap=False,
                                     axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                                     splitline_opts=opts.SplitLineOpts(is_show=False),
                                     split_number=20, min_="dataMin", max_="dataMax",
                                     axislabel_opts=opts.LabelOpts(is_show=False)),

            yaxis_opts=opts.AxisOpts(
                is_scale=True, splitline_opts=opts.SplitLineOpts(is_show=True),
            ),

            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            datazoom_opts=[
                opts.DataZoomOpts(is_show=False, type_="inside", xaxis_index=[0, 0], range_end=100),
                opts.DataZoomOpts(is_show=True, xaxis_index=[0, 1], pos_top="97%", range_end=100),
                opts.DataZoomOpts(is_show=True, xaxis_index=[0, 2], pos_top="97%", range_end=100),
                opts.DataZoomOpts(is_show=True, xaxis_index=[0, 3], pos_top="97%", range_end=100),
                opts.DataZoomOpts(is_show=False, xaxis_index=[0, 4], range_end=100),
            ],
            axispointer_opts=opts.AxisPointerOpts(is_show=True, label=opts.LabelOpts(formatter=JsCode(js_formatter))),



        )
    )

    kline_line = (
        Line()
        .add_xaxis(xaxis_data=data["times"])
        .add_yaxis(
            series_name="沪深300",
            yaxis_index=0,
            y_axis=calculate_ma(day_count=1),
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        # .set_global_opts(
        #     xaxis_opts=opts.AxisOpts(
        #         type_="category",
        #         grid_index=0,
        #         axislabel_opts=opts.LabelOpts(is_show=False),
        #     ),
        #     yaxis_opts=opts.AxisOpts(
        #         grid_index=0,
        #         split_number=3,
        #         axisline_opts=opts.AxisLineOpts(is_on_zero=False),
        #         axistick_opts=opts.AxisTickOpts(is_show=False),
        #         splitline_opts=opts.SplitLineOpts(is_show=False),
        #         axislabel_opts=opts.LabelOpts(is_show=True),
        #     ),
        # )
    )
    # Overlap Kline + Line
    overlap_kline_line = kline.overlap(kline_line)

    ## 货币供应量
    line_m2 = (
        Line()
        .add_xaxis(xaxis_data=data["times"])
        .add_yaxis(series_name="M0同比增长率",
                   y_axis=data['m0_yoy'],
                   xaxis_index=1,
                   yaxis_index=1,
                   label_opts=opts.LabelOpts(is_show=False),
                   )
        .add_yaxis(series_name="M1同比增长率",
                   y_axis=data['m1_yoy'],
                   xaxis_index=1,
                   yaxis_index=1,
                   label_opts=opts.LabelOpts(is_show=False),
                    )
        .add_yaxis(series_name="M2同比增长率",
                       y_axis=data['m2_yoy'],
                       xaxis_index=1,
                       yaxis_index=1,
                       label_opts=opts.LabelOpts(is_show=False),
                       )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True, pos_top="38%"),
            xaxis_opts=opts.AxisOpts(type_="category", grid_index=4, axislabel_opts=opts.LabelOpts(is_show=False)),
            yaxis_opts=opts.AxisOpts(grid_index=4, split_number=4, axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                                     axistick_opts=opts.AxisTickOpts(is_show=False),
                                     splitline_opts=opts.SplitLineOpts(is_show=True),
                                     axislabel_opts=opts.LabelOpts(is_show=True)),
        )

    )

    ## 利率
    line_shibor = (
        Line()
        .add_xaxis(xaxis_data=data["times"])
        .add_yaxis(series_name="shibor隔夜利率",
                   y_axis=data['shibor_on'],
                   xaxis_index=2,
                   yaxis_index=2,
                   label_opts=opts.LabelOpts(is_show=False),
                   )
        .add_yaxis(series_name="shibor1年利率",
                   y_axis=data['shibor_1y'],
                   xaxis_index=2,
                   yaxis_index=2,
                   label_opts=opts.LabelOpts(is_show=False),
                    )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True, pos_top="55%"),
            xaxis_opts=opts.AxisOpts(type_="category", grid_index=4, axislabel_opts=opts.LabelOpts(is_show=False)),
            yaxis_opts=opts.AxisOpts(grid_index=4, split_number=4, axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                                     axistick_opts=opts.AxisTickOpts(is_show=False),
                                     splitline_opts=opts.SplitLineOpts(is_show=True),
                                     axislabel_opts=opts.LabelOpts(is_show=True)),
        )
    )

    ## CPIandPPI
    line_cpi_ppi = (
        Line()
        .add_xaxis(xaxis_data=data["times"])
        .add_yaxis(series_name="CPI",
                   y_axis=data['cpi_nt_yoy'],
                   xaxis_index=3,
                   yaxis_index=3,
                   label_opts=opts.LabelOpts(is_show=False),
                   )
        .add_yaxis(series_name="PPI",
                   y_axis=data['ppi_yoy'],
                   xaxis_index=3,
                   yaxis_index=3,
                   label_opts=opts.LabelOpts(is_show=False),
                    )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True, pos_top="72%"),
            xaxis_opts=opts.AxisOpts(type_="category", grid_index=4, axislabel_opts=opts.LabelOpts(is_show=False)),
            yaxis_opts=opts.AxisOpts(grid_index=4, split_number=4, axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                                     axistick_opts=opts.AxisTickOpts(is_show=False),
                                     splitline_opts=opts.SplitLineOpts(is_show=True),
                                     axislabel_opts=opts.LabelOpts(is_show=True)),
        )

    )


    ## PE
    line_stack = (
        Line()
        .add_xaxis(xaxis_data=data["times"])
        .add_yaxis(series_name="pe_20_percentile",
                   stack='总量',
                   y_axis=[np.percentile(data["pe"], 20), ] * len(data['times']),
                   xaxis_index=4,
                   yaxis_index=4,
                   areastyle_opts=opts.AreaStyleOpts(opacity=0.5, color='white'),
                   label_opts=opts.LabelOpts(is_show=False),
                   )
        .add_yaxis(series_name="pe_80_percentile",
                    stack='总量',
                       y_axis=[np.percentile(data["pe"], 80) - np.percentile(data["pe"], 20), ] * len(data['times']),
                       xaxis_index=4,
                       yaxis_index=4,
                       areastyle_opts=opts.AreaStyleOpts(opacity=0.5, color='DarkRed'),
                       label_opts=opts.LabelOpts(is_show=False),
                       )

    )


    line_2 = (
        Line()
        .add_xaxis(xaxis_data=data["times"])
        .add_yaxis(
            series_name="pe",
            y_axis=data["pe"],
            xaxis_index=4,
            yaxis_index=4,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True, pos_top="84%"),
            xaxis_opts=opts.AxisOpts(type_="category", grid_index=4, axislabel_opts=opts.LabelOpts(is_show=True)),
            yaxis_opts=opts.AxisOpts(grid_index=4, split_number=4, axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                                     axistick_opts=opts.AxisTickOpts(is_show=False),
                                     splitline_opts=opts.SplitLineOpts(is_show=True),
                                     axislabel_opts=opts.LabelOpts(is_show=True)),
        )
    )
    # 最下面的柱状图和折线图
    overlap_line_area = line_2.overlap(line_stack)



    # 合并所有子图
    grid_chart = Grid(init_opts=opts.InitOpts(width="1400px", height="800px"))

    ## k
    grid_chart.add(overlap_kline_line,
                   grid_opts=opts.GridOpts(pos_left="3%", pos_right="1%", pos_top="5%", height="30%"),
                   )

    ## M2
    grid_chart.add(line_m2,
                   grid_opts=opts.GridOpts(pos_left="3%", pos_right="1%", pos_top="38%", height="14%" ),
                   )

    # SHIBOR
    grid_chart.add(line_shibor,
                   grid_opts=opts.GridOpts(pos_left="3%", pos_right="1%", pos_top="55%", height="14%"),
                   )

    ## cpi
    grid_chart.add(line_cpi_ppi,
                   grid_opts=opts.GridOpts(pos_left="3%", pos_right="1%", pos_top="72%", height="10%"),
                   )
    # PE
    grid_chart.add(overlap_line_area,
                   grid_opts=opts.GridOpts(pos_left="3%", pos_right="1%", pos_top="84%", height="10%"),
                   )

    ## 保存
    grid_chart.render("professional_kline_chart.html")


if __name__ == "__main__":
    ehcarts_data = pd.read_csv('data.csv', dtype=str)

    data = split_data(origin_data=ehcarts_data)

    draw_chart()