import os
import pandas as pd

from datetime import datetime

def 找符合要求的(判断条件, 停止 = lambda i, 代码: False):
  股票代号列表 = 获取股票代号列表()
  没有数据 = []
  结果 = []
  for idx, 股票代号 in enumerate(股票代号列表):
    if 停止(idx, 股票代号):
      break
    股票数据 = 获取股票数据(股票代号)
    if 股票数据.empty:
      没有数据.append(股票代号)
    个股结果 = 判断条件(股票数据)
    if 个股结果:
      结果.append(股票代号)
  return 结果

def 获取股票代号列表():
  股票列表 = pd.read_csv('./stock_list.csv')
  return [str(x['code']).zfill(6) for _, x in 股票列表.iterrows()]

def 获取股票代号名字映射():
  股票列表 = pd.read_csv('./stock_list.csv')
  结果 = {}
  for _, x in 股票列表.iterrows():
    结果[str(x['code']).zfill(6)] = x['name']
  return 结果

def 获取股票数据(股票代号: str):
  文件路径 = f'./data/{股票代号}.csv'
  if os.path.exists(文件路径):
    df = pd.read_csv(文件路径)
    if not df.empty:
      df['_日期'] = df['日期']
      df['日期'] = df['日期'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    return df
  return pd.DataFrame([])
