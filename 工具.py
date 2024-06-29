import os
import pandas as pd
import akshare as ak

from typing import List
from datetime import datetime

股票列表文件路径 = './stock_list.csv'
数据目录路径 = './data'
周数据目录路径 = './week_data'

MA参数 = [5, 10, 30, 60]
CLOSE_PRICE = '收盘'
MAX_PRICE = '最高'
MIN_PRICE = '最低'

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


def 获取股票数据(股票代号: str):
  文件路径 = f'./data/{股票代号}.csv'
  if os.path.exists(文件路径):
    df = pd.read_csv(文件路径)
    if not df.empty:
      df['_日期'] = df['日期']
      df['日期'] = df['日期'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
    return df
  return pd.DataFrame([])


def 获取历史数据(代号: str, 开始时间: str = None, 结束时间: str = None, 静态数据: bool = False, 周 = False):
  开始时间 = 开始时间 or '20210101'
  结束时间 = 结束时间 or datetime.now().strftime('%Y%m%d')
  period = 'weekly' if 周 else 'daily'
  静态数据目录路径 = 周数据目录路径 if 周 else 数据目录路径
  if 静态数据:
    df = pd.read_csv(f'{静态数据目录路径}{代号}.csv')
    开始时间 = datetime.strptime(开始时间, '%Y%m%d')
    结束时间 = datetime.strptime(结束时间, '%Y%m%d')
    日期 = df['日期'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    df = df[(日期 >= 开始时间) & (日期 <= 结束时间) ]
    return df
  
  return ak.stock_zh_a_hist(symbol=代号, start_date=开始时间, end_date=结束时间, adjust='qfq', period=period)


def 生成均线(df: pd.DataFrame, ns: List[int]):
  df = df.copy()
  for i in (ns or []):
    df[f'MA{i}'] = 计算均线(df, i)
  return df


def 计算均线(df: pd.DataFrame, n: int):
  return df[CLOSE_PRICE].rolling(window=n).mean()

# 数据获取
def 更新股票列表():
  股票列表 = ak.stock_info_a_code_name()
  股票列表.reset_index(drop=True, inplace=True)
  信息map = {}
  股票个数 = len(股票列表)
  for _i, code in enumerate(股票列表['code']):
    代号 = str(code).zfill(6)
    信息df = ak.stock_individual_info_em(代号)
    信息 = {}
    for i, x in 信息df.iterrows():
      信息[x['item']] = x['value']
    信息map[信息['股票代码']] = 信息
    print(f'获取信息中: {_i}/{股票个数}')

  for key in ['总市值', '流通市值', '行业', '总股本', '流通股']:
    股票列表[key] = 股票列表['code'].apply(lambda x: 信息map.get(str(x).zfill(6), {}).get(key, ''))

  股票列表.to_csv(股票列表文件路径, index=False)
  return 股票列表

def 获取股票信息(沪深 = False):
  股票列表 = pd.read_csv(股票列表文件路径)
  结果 = {}
  for _, x in 股票列表.iterrows():
    股票代号 = str(x['code']).zfill(6)
    if 沪深 and (股票代号[0] not in ['0', '6']):
      continue
    结果[股票代号] = x
  return 结果

def 获取股票代号名字映射(沪深 = False):
  return { k: v['name'] for k, v in 获取股票信息(沪深).items() }

def 获取股票代号列表(沪深 = False):
  股票代号名字映射 = 获取股票代号名字映射(沪深)
  return list(股票代号名字映射.keys())

def 更新股票数据(代号, MA参数 = MA参数, 周 = False):
  if 周:
    return 更新股票周数据(代号, MA参数 = MA参数)
  文件路径 = f'{数据目录路径}/{代号}.csv'
  数据 = 生成均线(获取历史数据(代号), MA参数)
  数据.reset_index(drop=True, inplace=True)
  数据.to_csv(文件路径, index=False)
  return 数据

def 更新股票周数据(代号, MA参数 = MA参数):
  文件路径 = f'{周数据目录路径}/{代号}.csv'
  数据 = 生成均线(获取历史数据(代号, 周=True), [4,8,16,24])
  数据.reset_index(drop=True, inplace=True)
  数据.to_csv(文件路径, index=False)
  return 数据