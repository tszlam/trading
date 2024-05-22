from datetime import datetime
from typing import List
import akshare as ak
import pandas as pd
import math

CLOSE_PRICE = '收盘'
MAX_PRICE = '最高'
MIN_PRICE = '最低'

def 计算均线(df: pd.DataFrame, n: int):
  return df[CLOSE_PRICE].rolling(window=n).mean()

def get_w_r(df: pd.DataFrame, n: int):
  H_n = df[MAX_PRICE].rolling(n).max()
  L_n = df[MIN_PRICE].rolling(n).min()
  return round(((H_n - df[CLOSE_PRICE]) / (H_n - L_n)) * (100), 2)

# 接口
# stock_zh_a_hist

def 获取历史数据(代号: str, 开始时间: str = None, 结束时间: str = None, 静态数据: bool = False):
  开始时间 = 开始时间 or '20210101'
  结束时间 = 结束时间 or datetime.now().strftime('%Y%m%d')
  if 静态数据:
    df = pd.read_csv(f'./data/{代号}.csv')
    开始时间 = datetime.strptime(开始时间, '%Y%m%d')
    结束时间 = datetime.strptime(结束时间, '%Y%m%d')
    日期 = df['日期'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    df = df[(日期 >= 开始时间) & (日期 <= 结束时间) ]
    return df
  return ak.stock_zh_a_hist(symbol=代号, start_date=开始时间, end_date=结束时间, adjust='qfq')

def 生成均线(df: pd.DataFrame, ns: List[int]):
  df = df.copy()
  for i in (ns or []):
    df[f'MA{i}'] = 计算均线(df, i)
  return df

def get_hist_df(sym: str, start_date: str = None, end_date: str = None, mas: List[int] = None):
  return 生成均线(获取历史数据(代号=sym, 开始时间=start_date, 结束时间=end_date), mas)


def run_all_in_sim(df: pd.DataFrame, cny: int = 100000, 止盈: float = 10000, 止亏: float = 1):
  def buy(prx: float, cny: float):
    unit_prx = prx * 100
    qty = math.floor(cny / unit_prx)
    return cny - (qty * unit_prx), qty
  
  def sell(prx: float, cny: float, qty: int):
    return cny + (prx * qty * 100), 0
  
  init_cny = cny
  cur_cny = init_cny
  cur_qty = 0
  df = df.copy()
  df.sort_values('日期', ascending=True, inplace=True)

  交易记录 = [{
    '数量': cur_qty,
    '资金': init_cny,
    '市值': init_cny,
  }]
  已买入 = None
  for _, x in df.iterrows():
    if 已买入:
      # 找卖点
      卖出价 = x['卖出价']
      卖出类型 = '信号'
      if x['卖出点'] == 0:
        # 需不需止盈/止亏
        最大盈亏 = (x['最高'] - 已买入['价格']) / 已买入['价格']
        最小盈亏 = (x['最低'] - 已买入['价格']) / 已买入['价格']
        if 最大盈亏 > 止盈:
          卖出价 = 已买入['价格'] * (1 + 止盈)
          卖出类型 = '止盈'
        elif 最小盈亏 < -止亏:
          卖出价 = 已买入['价格'] * (1 - 止亏)
          卖出类型 = '止亏'
        else:
          continue
      cur_cny, cur_qty = sell(卖出价, cur_cny, cur_qty)
      交易记录.append({
        '买入日期': 已买入['日期'],
        '卖出日期': x['日期'],
        '买入价': 已买入['价格'],
        '卖出价': 卖出价,
        '数量': 已买入['数量'],
        '资金': cur_cny,
        '市值': cur_cny,
        '卖出类型': 卖出类型
      })
      已买入 = None
    else:
      # 找买点
      if x['买入点'] == 0:
        continue
      cur_cny, cur_qty = buy(x['买入价'], cur_cny)
      已买入 = {
        '日期': x['日期'],
        '价格': x['买入价'],
        '数量': cur_qty
      }

  交易次数 = len(交易记录)

  if 已买入:
    交易记录.append({
      '买入日期': 已买入['日期'],
      '卖出日期': None,
      '买入价': 已买入['价格'],
      '卖出价': None,
      '数量': 已买入['数量'],
      '资金': cur_cny,
      '市值': df.iloc[-1]['收盘'] * 100 * 已买入['数量'] + cur_cny
    })

  if len(交易记录) == 1:
    # 只有用来记录初始数据的dummy记录 - 没有交易
    return {
    '本金': init_cny,
    '盈亏': 0,
    '盈亏比例': 0,
    '交易记录': pd.DataFrame([]),
    '交易次数': 0
    }
  
  总盈亏 = 交易记录[-1]['市值'] - init_cny
  总盈亏比例 = round((总盈亏 / init_cny) * 100, 2)
  交易记录.append({'总盈亏': 总盈亏, '总盈亏%': 总盈亏比例})

  交易记录_df = pd.DataFrame(交易记录)
  交易前市值 = 交易记录_df['市值'].shift(1)
  交易记录_df['盈亏'] = 交易记录_df['市值'] - 交易前市值
  交易记录_df['盈亏%'] = round((交易记录_df['盈亏'] / 交易前市值) * 100, 2)
  交易记录_df = 交易记录_df.iloc[1:][['买入日期','卖出日期','买入价','卖出价','卖出类型','数量','资金','市值', '盈亏', '盈亏%', '总盈亏', '总盈亏%']]

  return {
    '本金': init_cny,
    '盈亏': 总盈亏,
    '盈亏比例': 总盈亏比例,
    '交易记录': 交易记录_df,
    '交易次数': 交易次数
  }

def 生成买卖点_基础(df: pd.DataFrame, 买入准备, 买入, 买入价, 卖出准备, 卖出, 卖出价):
  '''
  这个方法的买入/卖出准备是有持久性的，为真之后就一定会买/卖
  '''
  df = df.copy()
  准备买, 准备卖, 买入日期, 卖出日期, 当前买入 = False, False, [], [], None
  for _, x in df.iterrows():
    if not 准备买:
      准备买 = 买入准备(x)
    if 准备买:
      if 买入(x):
        买入日期.append(x['日期'])
        当前买入 = x
        准备买 = False

    if not 准备卖:
      准备卖 = 卖出准备(x, 当前买入)
    if 准备卖:
      if 卖出(x, 当前买入):
        卖出日期.append(x['日期'])
        当前买入 = None
        准备卖 = False

  df['买入点信号'] = df['日期'].isin(买入日期).astype(int)
  df['买入点'] = (df['买入点信号'].shift(1) == 1).astype(int)
  df['卖出点信号'] = df['日期'].isin(卖出日期).astype(int)
  df['卖出点'] = (df['卖出点信号'].shift(1) == 1).astype(int)
  
  df['买入价'] = df.apply(买入价, axis=1)
  df['卖出价'] = df.apply(卖出价, axis=1)

  return df