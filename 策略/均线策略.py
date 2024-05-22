import pandas as pd
from typing import List
from utils import 获取历史数据, 生成均线, 生成买卖点_基础, run_all_in_sim

静态数据 = True
开始时间 = '20230101'
止盈阈值 = 0.05
止亏阈值 = 0.05
模拟列 = [
  '日期',
  '买入点',
  '买入价',
  '卖出点',
  '卖出价',
  '收盘',
  '最高',
  '最低'
]
def 生成均线相关(df: pd.DataFrame, 均线参数):
  df = df.copy()
  均线Key = f'MA{均线参数}'
  前一日均线Key = f'{均线Key}-1'
  df[前一日均线Key] = df[均线Key].shift(1)
  df['方向'] = df.apply(lambda x: 0 if x[均线Key] == x[前一日均线Key] else (1 if x[均线Key] > x[前一日均线Key] else -1), axis=1)
  df = df[df['方向']!=0]
  df['方向-1'] = df['方向'].shift(1)
  df.dropna(inplace=True)
  return df


买入价 = lambda x: x['开盘']
卖出价 = lambda x: x['开盘']
def 单均线策略生成(均线参数, 买入准备, 买入, 卖出准备, 卖出):
  def x(df: pd.DataFrame):
    df = 生成均线(df, [均线参数])
    df = 生成均线相关(df, 均线参数)
    df = 生成买卖点_基础(df, 买入准备, 买入, 买入价, 卖出准备, 卖出, 卖出价)
    return df[模拟列]
  return x

sty = {
 '均线_1': 单均线策略生成(
    5,
    lambda x: x['方向-1'] == -1 and x['方向'] == 1,
    lambda x: True,
    lambda x, y: (x['方向-1'] == 1 and x['方向'] == -1),
    lambda x, y: True,
  ),
}

def 单个测试(stock):
  df = 获取历史数据(stock, 开始时间=开始时间, 静态数据=静态数据)
  print(f'\n====== [{stock}] ======')
  for name, func in sty.items():
    # res = run_all_in_sim(func(df), 止盈=0.1, 止亏=0.1)
    res = run_all_in_sim(func(df), 止亏=0.1)
    print(f'\n{name}: {res["盈亏比例"]}%')
    print(res['交易记录'].to_string())

单个测试('600887')

def 批量测试():
  test_list = [
    '601919',
    '601138',
    '600522',
    '601838',
    '001979',
    '600887',
    '000001',
    '002311',
    '601899',
    '601288',
  ]
  for stock in test_list:
    df = 获取历史数据(stock, 开始时间=开始时间, 静态数据=静态数据)
    msg = f'\n====== [{stock}] ======'
    for name, func in sty.items():
      # res = run_all_in_sim(func(df), 止盈=0.1, 止亏=0)
      res = run_all_in_sim(func(df), 止亏=0)
      # res = run_all_in_sim(func(df))
      msg += f'\n{name}: {res["盈亏比例"]}%'
    print(msg)

# 批量测试()