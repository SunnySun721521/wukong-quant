#!/usr/bin/env python3
import sys
import os
import json

# 直接测试文件读取
stock_pool_file = "logs/stock_pool.json"
print(f"Current directory: {os.getcwd()}")
print(f"Stock pool file: {stock_pool_file}")
print(f"File exists: {os.path.exists(stock_pool_file)}")

if os.path.exists(stock_pool_file):
    with open(stock_pool_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"Loaded data type: {type(data)}")
        print(f"Loaded data keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
        stocks = data.get('stocks', [])
        print(f"Stocks from file: {stocks}")
        print(f"Stocks count: {len(stocks)}")
else:
    print("File does not exist")