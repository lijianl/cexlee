import json

import ccxt

# 数据获取 -> 指标建设 -> 信号生成 -> 数据回测
apikey = "0f78782e-b3be-4be8-ad01-d0ee127c0a18"
secretkey = "2CBE3955F5D5391EDD7F663998A6ECD8"
PASSPHRASE = "Lennie#002"

exchange = ccxt.okx({
    'enableRateLimit': True,
})


def getBalance():
    # 获取账户余额
    balance = exchange.fetch_balance()
    print('账户余额信息:', balance)


def getTicker() -> dict:
    # 获取ETH/USDT的Ticker数据
    print(exchange.fetch_markets())
    print(exchange.markets)
    ticker = exchange.fetch_ticker('ETH-USDT')
    return ticker


def getMarkets():
    global exchange
    exchange = ccxt.okx()
    markets = exchange.fetch_markets()
    # 保存到文件
    with open('okx_markets.json', 'w') as f:
        json.dump(markets, f)
    # 之后在离线环境中加载
    with open('okx_markets.json', 'r') as f:
        markets = json.load(f)
    # 手动设置市场数据
    exchange.set_markets(markets)




if __name__ == '__main__':
    print(exchange.fetch_time())
    getMarkets()
    # getTicker()
