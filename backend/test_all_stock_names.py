import requests
import json

r = requests.get('http://localhost:5006/api/stockpool/info')
data = json.loads(r.text)

print('当前股票池信息:')
print(f'股票数量: {data.get("pool_size", 0)}')
print(f'最后更新: {data.get("last_updated", "未知")}')
print()

print('股票列表及名称:')
for stock in data.get('stock_details', []):
    symbol = stock['symbol']
    name = stock['name']
    print(f'{symbol}: {name}')

print()
print('检查是否有股票显示为默认格式 "股票{code}":')
has_default = False
for stock in data.get('stock_details', []):
    if stock['name'].startswith('股票'):
        print(f'  {stock["symbol"]}: {stock["name"]}')
        has_default = True

if not has_default:
    print('  所有股票名称都已正确映射！')
