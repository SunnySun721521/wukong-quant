#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

from strategy.data_provider import DataProvider

print("=== 测试股票003816的信息获取 ===")

symbol = "003816"

# 测试1: 获取股票信息
print("\n1. 测试获取股票信息:")
stock_info = DataProvider.get_stock_info(symbol)
print(f"   股票信息: {stock_info}")
if stock_info:
    print(f"   股票名称: {stock_info.get('name', 'N/A')}")
    print(f"   股票价格: {stock_info.get('price', 'N/A')}")

# 测试2: 获取当前价格
print("\n2. 测试获取当前价格:")
current_price = DataProvider.get_current_price(symbol)
print(f"   当前价格: {current_price}")

# 测试3: 检查是否为A股
print("\n3. 检查股票类型:")
is_a_stock = DataProvider.is_a_stock(symbol)
print(f"   是否为A股: {is_a_stock}")

# 测试4: 尝试获取K线数据
print("\n4. 测试获取K线数据:")
from datetime import datetime
end_date = datetime.now().strftime('%Y%m%d')
start_date = '20250101'
kline_data = DataProvider.get_kline_data(symbol, start_date, end_date)
if kline_data is not None:
    print(f"   K线数据获取成功，共{len(kline_data)}条记录")
else:
    print(f"   K线数据获取失败")

print("\n=== 测试完成 ===")