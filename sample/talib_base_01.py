## 安装talib
# brew upgrade
# brew insatll ta-lib
# pip install ta-lib
# pip install backtrader


### 通过配置文件
#  ~/.pip/pip.conf  ||  ~/.config/pip/pip.conf
# pip install backtrader --index-url http://mirrors.aliyun.com/pypi/simple/ --trusted-host trusted-host=mirrors.aliyun.com

### 通过指令配置文件, 可是使用阿里云库
# pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
# pip config set global.trusted-host mirrors.aliyun.com
# pip config list

import talib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 生成示例数据
np.random.seed(0)
# 这里返回，正态分布随机数
base_prices = np.random.randn(100)
# 累计求和, 模拟股票价格
close_prices = base_prices.cumsum() + 100
df = pd.DataFrame({'close': close_prices})
# 计算10日简单移动平均线, 第11个开始
sma_10 = talib.SMA(df['close'], timeperiod=10)

# 绘制收盘价和10日简单移动平均线
plt.figure(figsize=(12, 6))

# 曲线标题
plt.plot(df['close'], label='Close Price')
plt.plot(sma_10, label='10-day SMA')
plt.title('Close Price and 10-day SMA')
plt.xlabel('Period')
plt.ylabel('Price')
plt.legend()
plt.show()
