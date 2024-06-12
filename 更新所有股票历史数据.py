import os
import pandas as pd
from utils import 获取历史数据

股票列表 = pd.read_csv('./stock_list.csv')
total = len(股票列表)

def 将文件的日期转成接口日期(日期):
  年, 月, 日 = 日期.split('-')
  return 年+月+日

for i, x in 股票列表.iterrows():
  股票代码: str = str(x['code']).zfill(6)
  # 只要沪深的
  if (not 股票代码.startswith('0')) and (not 股票代码.startswith('6')):
    continue
  文件路径 = f'./data/{股票代码}.csv'
  if os.path.exists(文件路径):
    # 补全数据
    历史df = pd.read_csv(文件路径)
    日期 = 历史df.sort_values('日期', ascending=False, inplace=False).iloc[0]['日期']
    增量df = 获取历史数据(股票代码, 开始时间=将文件的日期转成接口日期(日期))
    pd.concat([历史df,增量df]).drop_duplicates().to_csv(文件路径, index=False)
  else:
    # 获取历史数据
    获取历史数据(股票代码).to_csv(文件路径, index=False)
  print(f'进度: {i+1} / {total}')