import math
import pandas as pd
from utils import 获取历史数据, get_w_r, run_all_in_sim, 生成买卖点_基础, 生成均线

开始时间 = '20220101'
静态数据 = True
快慢贴合阈值 = 3
稳定粘连阈值 = 5 # 天
买卖稳定阈值 = 5 # 天
买入点窗口 = 3 # 天
超卖阈值 = 80
超买阈值 = 20
稳定波动阈值 = 15
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
调试列 = [
  '日期',
  # '开盘',
  # '收盘',
  'WR_21',
  'WR_42',
  # '超卖_21',
  # '超卖_42',
  # '超卖',
  'WR_diff',
  '是否粘连',
  '粘连持续',
  '超卖持续',
  '超卖稳定',
  # '收阳',
  # '买入点信号',
  '买入点',
  # '买入价',
  # '超买_21',
  # '超买_42',
  # '超买',
  # '不超买',
  # '卖出点信号',
  '卖出点',
  # '卖出价'
]

快参数 = 21
慢参数 = 42
def 处理威廉指标_通用(df: pd.DataFrame, **参数):
  df = df.copy()
  _快参数 = 参数.get('快', 快参数)
  _慢参数 = 参数.get('慢', 慢参数)
  df['WR_快'] = get_w_r(df, _快参数)
  df['WR_慢'] = get_w_r(df, _慢参数)
  df.dropna(inplace=True)
  df['WR_快慢差值'] = abs(df['WR_快'] - df['WR_慢'])

  return df

def 处理威廉指标_额外(df: pd.DataFrame, **参数):
  df = df.copy()
  _快慢贴合阈值 = 参数.get('快慢贴合阈值', 快慢贴合阈值)
  _超卖阈值 = 参数.get('超卖阈值', 超卖阈值)
  _超买阈值 = 参数.get('超买阈值', 超买阈值)
  df['WR_快慢贴合'] = (df['WR_快慢差值'] < _快慢贴合阈值).astype(int)
  # 超卖
  df['WR_超卖_快'] = (df['WR_快'] >= _超卖阈值).astype(int)
  df['WR_超卖_慢'] = (df['WR_慢'] >= _超卖阈值).astype(int)
  df['WR_超卖'] = (df['WR_超卖_快'] + df['WR_超卖_慢'] == 2).astype(int)
  # 超买
  df['WR_超买_快'] = (df['WR_快'] <= _超买阈值).astype(int)
  df['WR_超买_慢'] = (df['WR_慢'] <= _超买阈值).astype(int)
  df['WR_超买'] = (df['WR_超买_快'] + df['WR_超买_慢'] == 2).astype(int)
  # df.dropna(inplace=True)

  return df
  

def 处理威廉指标(df: pd.DataFrame):
  df['WR_21'] = get_w_r(df, 21)
  df['WR_42'] = get_w_r(df, 42)
  df.dropna(inplace=True)
  # WR_21_ytd = df['WR_21'].shift(1)
  # WR_42_ytd = df['WR_42'].shift(1)

  # 买点判断数据处理
  df['超卖_21'] = (df['WR_21'] >= 超卖阈值).astype(int)
  df['超卖_42'] = (df['WR_42'] >= 超卖阈值).astype(int)
  df['超卖'] = ((df['超卖_21'] + df['超卖_42']) == 2).astype(int)
  df['不超卖'] = ((df['超卖_21'] + df['超卖_42']) == 0).astype(int)
  
  df['WR_diff'] = abs(df['WR_21'] - df['WR_42']).apply(lambda x: math.ceil(x))
  df['是否粘连'] = (df['WR_diff'] < 快慢贴合阈值).astype(int)
  df[f'粘连持续'] = (df['是否粘连'].rolling(稳定粘连阈值).mean() == 1).astype(int)
  df[f'超卖持续'] = (df['超卖'].rolling(买卖稳定阈值).mean() == 1).astype(int)
  df['超卖稳定'] = ((df[f'粘连持续'] + df[f'超卖持续']) == 2).astype(int)
  df['收阳'] = ((df['收盘'] - df['开盘']) > 0).astype(int)

  # 卖点判断数据处理
  df['超买_21'] = (df['WR_21'] <= 超买阈值).astype(int)
  df['超买_42'] = (df['WR_42'] <= 超买阈值).astype(int)
  df['超买'] = ((df['超买_21'] + df['超买_42']) == 2).astype(int)
  df['不超买'] = ((df['超买_21'] + df['超买_42']) == 0).astype(int)

  return df

def 威廉指标策略_生成(均线参数, 买入准备, 买入, 卖出准备, 卖出):
  def x(stock: str):
    df = 获取历史数据(stock,开始时间=开始时间,静态数据=静态数据)
    df = 生成均线(df, 均线参数)
    df = 处理威廉指标(df)
    买入价 = lambda x: x['开盘']
    卖出价 = lambda x: x['开盘']
    df = 生成买卖点_基础(df, 买入准备, 买入, 买入价, 卖出准备, 卖出, 卖出价)

    # df[调试列].to_csv('./调试.csv', index=False)
    return df[模拟列]
  return x

威廉指标策略_1 = 威廉指标策略_生成(
    [10],
    lambda x: x['超卖稳定'] == 1,
    lambda x: x['收阳'] == 1 and x['不超卖'] == 1,
    lambda x, y: x['超买'] == 1,
    lambda x, y: x['不超买'] == 1 or x['MA10'] < x['收盘'], # 里看下 MA10 是要按最低还是收盘
  )

威廉指标策略_2 = 威廉指标策略_生成(
    [10],
    lambda x: x['超卖稳定'] == 1,
    lambda x: x['收阳'] == 1 and x['不超卖'] == 1,
    lambda x, y: x['超买_21'] == 1 or x['超买_42'] == 1,
    lambda x, y: x['不超买'] == 1 or x['MA10'] < x['收盘'], # 里看下 MA10 是要按最低还是收盘
  )

def 批量测试():
  test_list = [
    # '601919',
    # '601138',
    # '600522',
    # '601838',
    # '001979',
    # '600887',
    # '000001',
    # '002311',
    # '601899',
    # '601288',
    '000661',
    '603688',
    '301589',
    '002304',
    '600519',
    '600809',
    '000858',
    '000596',
    '000568',
    '688169',
  ]
  sty = {
   '威廉指标策略_1': 威廉指标策略_1, 
   '威廉指标策略_2': 威廉指标策略_2, 
  }
  for stock in test_list:
    msg = f'\n====== [{stock}] ======'
    for name, func in sty.items():
      data = func(stock)
      res = run_all_in_sim(data)
      msg += f'\n{name}: {res["盈亏比例"]}%'
    print(msg)

# 批量测试()

def 单个测试(stock):
  sty = {
   '威廉指标策略_1': 威廉指标策略_1, 
   '威廉指标策略_2': 威廉指标策略_2, 
  }
  print(f'\n====== [{stock}] ======')
  for name, func in sty.items():
    res = run_all_in_sim(func(stock), 止盈=0.2)
    # res = run_all_in_sim(func(stock))
    print(f'\n{name}: {res["盈亏比例"]}%')
    print(res['交易记录'].to_string())

# 单个测试('603688')