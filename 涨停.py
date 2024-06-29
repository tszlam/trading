from datetime import datetime
from 工具 import (
  获取股票代号列表,
  获取股票代号名字映射,
  获取股票数据,
)

股票代号名字映射 = 获取股票代号名字映射()
沪深股票代号列表 = [x for x in 获取股票代号列表() if x.startswith('0') or x.startswith('6')]

这个月涨停的股票 = []
这个月开始日期 = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)

for 代号 in 沪深股票代号列表:
  股票数据 = 获取股票数据(代号)
  股票数据 = 股票数据[股票数据['日期'] >= 这个月开始日期]
  股票数据 = 股票数据[股票数据['涨跌幅'] > 9]
  if len(股票数据) > 1:
    这个月涨停的股票.append(代号)

print(len(这个月涨停的股票))
print(这个月涨停的股票)