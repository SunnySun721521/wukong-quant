#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
from strategy.data_provider import DataProvider

symbols = ['600519', '000858', '002371', '002415', '002236']

print("开始测试数据获取...")
for symbol in symbols:
    print(f"\n测试股票: {symbol}")
    df = DataProvider.get_kline_data(symbol, '20240101', '20250111')
    if df is not None:
        print(f"  数据获取成功！")
        print(f"  数据形状: {df.shape}")
        print(f"  数据列: {df.columns.tolist()}")
        print(f"  前3行:")
        print(df.head(3))
    else:
        print(f"  数据获取失败！")

print("\n测试完成！")