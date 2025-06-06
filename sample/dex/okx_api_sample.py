import ccxt

# 数据获取 -> 指标建设 -> 信号生成 -> 数据回测
apikey = "0f78782e-b3be-4be8-ad01-d0ee127c0a18"
secretkey = "2CBE3955F5D5391EDD7F663998A6ECD8"
PASSPHRASE = "Lennie#002"

exchange = ccxt.okx({
    'apiKey': apikey,
    'secret': secretkey,
    'password': PASSPHRASE,
    'enableRateLimit': True,
})

# 获取账户余额
balance = exchange.fetch_balance()
print('账户余额信息:', balance)

symbol = 'BTC/USDT'
try:
    ticker = exchange.fetch_ticker(symbol)
    print(f'{symbol}的行情信息:', ticker)
except ccxt.NetworkError as e:
    print(f'网络错误: {e}')
except ccxt.ExchangeError as e:
    print(f'交易所错误: {e}')
