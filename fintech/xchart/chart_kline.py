import pyecharts
# print(pyecharts.__version__)
from pyecharts.charts import Kline
from pyecharts import options as opts
import pandas as pd
import datetime


def make_kline_v1():
    # 1. 准备数据,open,close,high,low
    data = [
        [2320.26, 2320.26, 2287.3, 2362.94],
        [2300, 2291.3, 2288.26, 2308.38],
        [2295.35, 2346.5, 2295.35, 2345.92],
        [2347.22, 2358.98, 2337.35, 2363.8],
    ]
    # 配置 Kline 图
    kline = (
        Kline()
        .add_xaxis(xaxis_data=["2017-10-24", "2017-10-25", "2017-10-26", "2017-10-27"])
        .add_yaxis(series_name="Kline", y_axis=data)
        .set_global_opts(
            # 刻度自适应
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(is_scale=True),
            title_opts=opts.TitleOpts(title="Kline 示例"),
        )
    )

    # 渲染图表，输出到html文件中,当前目录
    kline.render("kline_chart.html")


def make_kline_v2():
    '''
    数据处理
    '''
    df = pd.read_csv('../../data/okx_ETH-USDT_5m_20250101_20250629.csv')
    # 如果是毫秒时间戳，需要先除以1000
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    # 步骤2：将datetime对象格式化为文本时间
    df['time_text'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    y_data = df['time_text'].tolist()
    x_data = df[['open', 'close', 'high', 'low']].values.tolist()
    kline = (
        Kline(init_opts=opts.InitOpts(
            width="1400px",  # 增加图表宽度
            height="1000px",  # 增加图表高度
        ))
        .add_xaxis(xaxis_data=y_data)
        .add_yaxis(series_name="Kline", y_axis=x_data)
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(is_scale=True),
            title_opts=opts.TitleOpts(title="ETH/USDT"),
            # 数据缩放 - 修改为显示全部数据
            datazoom_opts=[
                # 内部缩放组件，支持鼠标滚轮在x轴上缩放
                opts.DataZoomOpts(
                    is_show=True,
                    type_="inside",
                    range_start=0,
                    range_end=100,
                    orient="horizontal",
                    xaxis_index=[0],
                    # 只在x轴上启用缩放
                ),
                # 滑块型数据缩放组件
                opts.DataZoomOpts(
                    is_show=True,
                    type_="slider",
                    range_start=0,
                    range_end=100,
                    orient="horizontal",
                    xaxis_index=[0],
                    # 设置滑块的位置在底部
                    pos_bottom="10%",
                )
            ],
            # 工具盒
            toolbox_opts=opts.ToolboxOpts(
                feature={
                    "dataZoom": {"yAxisIndex": "none"},
                    "restore": {},
                    "saveAsImage": {},
                }
            ),
        )
    )
    # 渲染图表
    kline.render("eth-usdt_kline_chart.html")


if __name__ == '__main__':
    make_kline_v2()
