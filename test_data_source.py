#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据源连接状态
"""
import sys
import os

# 添加策略目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategy'))

print('=== 测试数据源连接 ===')
print()

# 测试股票 002371
test_symbol = '002371'

print(f'1. 测试 DataProvider.get_current_price():')
try:
    from data_provider import DataProvider
    price = DataProvider.get_current_price(test_symbol)
    if price:
        print(f'   ✓ 成功获取价格: {price}')
    else:
        print(f'   ✗ 获取失败，返回 None')
except Exception as e:
    print(f'   ✗ 调用失败: {e}')

print()
print('2. 测试 akshare 数据源:')
try:
    import akshare as ak
    df = ak.stock_zh_a_spot_em()
    if df is not None and not df.empty:
        print(f'   ✓ akshare 连接成功，获取到 {len(df)} 只股票数据')
        stock_df = df[df['代码'] == test_symbol]
        if not stock_df.empty:
            ak_price = float(stock_df['最新价'].values[0])
            print(f'   ✓ 找到股票 {test_symbol}，价格: {ak_price}')
        else:
            print(f'   ✗ 未找到股票 {test_symbol}')
    else:
        print(f'   ✗ akshare 返回空数据')
except Exception as e:
    print(f'   ✗ akshare 连接失败: {e}')

print()
print('3. 测试 efinance 数据源:')
try:
    import efinance as ef
    df = ef.stock.get_realtime_quotes()
    if df is not None and not df.empty:
        print(f'   ✓ efinance 连接成功，获取到 {len(df)} 只股票数据')
        df.columns = df.columns.str.replace(' ', '')
        stock_df = df[df['股票代码'] == test_symbol]
        if not stock_df.empty:
            ef_price = float(stock_df['最新价'].values[0])
            print(f'   ✓ 找到股票 {test_symbol}，价格: {ef_price}')
        else:
            print(f'   ✗ 未找到股票 {test_symbol}')
    else:
        print(f'   ✗ efinance 返回空数据')
except Exception as e:
    print(f'   ✗ efinance 连接失败: {e}')

print()
print('=== 测试完成 ===')
