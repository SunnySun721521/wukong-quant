import csv
import os

position_file = 'd:\\trae\\备份悟空52216\\strategy\\data\\position_data.csv'
held_stocks = []
try:
    if os.path.exists(position_file):
        with open(position_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for pos in reader:
                held_stocks.append(pos['symbol'])
except Exception as e:
    print(f'读取持仓数据失败: {e}')
print(f'当前持仓股票: {held_stocks}')
print(f'宁德时代(300750)是否在持仓中: {"300750" in held_stocks}')
print(f'上海建工(600170)是否在持仓中: {"600170" in held_stocks}')