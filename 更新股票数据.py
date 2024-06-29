import os
from 工具 import 更新股票数据, 获取股票代号列表, 更新股票列表, 更新股票周数据, 数据目录路径, 周数据目录路径

更新股票列表()

print('开始删除历史数据')

for 文件名 in os.listdir(数据目录路径):
  文件路径 = os.path.join(数据目录路径, 文件名)
  os.unlink(文件路径)
for 文件名 in os.listdir(周数据目录路径):
  文件路径 = os.path.join(周数据目录路径, 文件名)
  os.unlink(文件路径)
print('删除历史数据完成')


股票列表 = 获取股票代号列表(沪深=False)
股票总数 = len(股票列表)
print('开始获取数据...')
for i, 代号 in enumerate(股票列表):
  更新股票数据(代号)
  更新股票周数据(代号)
  print(f'进度: {i+1} / {股票总数}')
  
print('完成')