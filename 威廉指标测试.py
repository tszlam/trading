import pandas as pd

from datetime import datetime
from 威廉指标策略 import 处理威廉指标_通用
from 工具 import 获取股票数据, 找符合要求的, 获取股票代号名字映射
from utils import 获取历史数据

股票代号名字映射 = 获取股票代号名字映射()

def 找贴合超卖(df: pd.DataFrame):
  df = 处理威廉指标_通用(df)
  快慢贴合阈值 = 0.1
  超卖阈值 = 80
  df = df[(
    (df['WR_快慢差值'] < 快慢贴合阈值) & 
    (df['WR_快'] > 超卖阈值) & 
    (df['WR_慢'] > 超卖阈值)
  )]
  if not df.empty:
    开始时间 = datetime(2024,5,20)
    df = df[df['日期'] >= 开始时间]
    # df = df[df['日期'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d')) >= 开始时间]
  return not df.empty
  # return df

结果 = 找符合要求的(找贴合超卖)
# 只要沪深非ST的
结果 = [x for x in 结果 if not 股票代号名字映射[x].startswith('ST') and not x.startswith('8')]
print(结果)

# print(找贴合超卖(获取历史数据('301322', 静态数据=False)))