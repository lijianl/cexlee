import ccxt
import pandas as pd
import time
import os
from datetime import datetime, timedelta

def fetch_binance_kline_data(symbol: str, timeframe: str, start_date: str, end_date: str = None, limit: int = 1000, save_csv: bool = True) -> pd.DataFrame:
    """
    从币安交易所获取K线历史数据

    参数:
        symbol (str): 交易对，例如 "BTC/USDT"
        timeframe (str): 时间周期，例如 "1m", "5m", "1h", "1d"
        start_date (str): 开始日期，格式 "YYYY-MM-DD"
        end_date (str, optional): 结束日期，格式 "YYYY-MM-DD". 默认是当前日期
        limit (int, optional): 每次请求的数据条数，最大为1000
        save_csv (bool, optional): 是否保存为CSV文件

    返回:
        pd.DataFrame: 包含K线数据的DataFrame
    """
    # 初始化币安交易所对象
    exchange = ccxt.binance({
        'enableRateLimit': True,  # 启用速率限制
        'options': {
            'defaultType': 'spot',  # 默认交易类型为现货
        }
    })

    # 转换日期格式
    start_timestamp = exchange.parse8601(f"{start_date}T00:00:00Z")

    if end_date:
        end_timestamp = exchange.parse8601(f"{end_date}T23:59:59Z")
    else:
        end_timestamp = exchange.milliseconds()  # 当前时间

    # 存储所有K线数据
    all_ohlcv = []

    # 循环获取数据直到获取完所有指定时间范围的数据
    current_timestamp = start_timestamp
    while current_timestamp < end_timestamp:
        try:
            # 获取K线数据
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, current_timestamp, limit)

            if not ohlcv:
                break

            # 更新当前时间戳为下一个请求的起始时间
            current_timestamp = ohlcv[-1][0] + 1

            # 存储数据
            all_ohlcv.extend(ohlcv)

            # 避免触发API速率限制
            time.sleep(exchange.rateLimit / 1000)

            # 打印进度
            progress = min(current_timestamp, end_timestamp) / end_timestamp * 100
            print(f"\r进度: {progress:.2f}%", end="")

        except Exception as e:
            print(f"\n错误: {e}")
            print(f"暂停10秒后继续...")
            time.sleep(10)

    print("\n数据获取完成!")

    if not all_ohlcv:
        print("未获取到任何数据")
        return pd.DataFrame()

    # 转换为DataFrame
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # 转换时间戳为可读格式
    df['datetime'] = df['timestamp'].apply(lambda x: exchange.iso8601(x))

    # 重新排列列顺序
    df = df[['datetime', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]

    # 保存为CSV
    if save_csv:
        # 创建数据文件夹（如果不存在）
        if not os.path.exists('data'):
            os.makedirs('data')

        # 生成文件名
        filename = f"data/binance_{symbol.replace('/', '-')}_{timeframe}_{start_date.replace('-', '')}_{datetime.now().strftime('%Y%m%d')}.csv"

        # 保存数据
        df.to_csv(filename, index=False)
        print(f"数据已保存到: {filename}")

    return df

if __name__ == "__main__":
    # 示例：获取BTC/USDT的4小时K线数据，从2023年1月1日到现在
    df = fetch_binance_kline_data(
        symbol="ETH/USDT",
        timeframe="1h",
        start_date="2025-05-01",
        end_date=None,  # 默认到当前日期
        limit=1000,
        save_csv=True
    )

    # 打印数据基本信息和前几行
    if not df.empty:
        print(df.info())
        print(df.head())