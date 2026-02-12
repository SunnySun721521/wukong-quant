#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

from strategy.data_provider import DataProvider

print("=== 测试修改后的股票信息获取 ===")

symbol = "003816"

# 测试获取股票信息
print(f"\n测试获取股票 {symbol} 的信息:")
stock_info = DataProvider.get_stock_info(symbol)
print(f"股票信息: {stock_info}")
if stock_info:
    print(f"股票代码: {stock_info.get('symbol', 'N/A')}")
    print(f"股票名称: {stock_info.get('name', 'N/A')}")
    print(f"股票价格: {stock_info.get('price', 'N/A')}")
else:
    print("获取股票信息失败")

print("\n=== 测试完成 ===")