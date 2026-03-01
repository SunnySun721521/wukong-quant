#!/usr/bin/env python3
import sys
import os
import json
sys.path.append(os.path.dirname(__file__))

from strategy.stock_pool_manager import StockPoolManager

# 测试StockPoolManager的加载
log_dir = "../logs"
manager = StockPoolManager(log_dir=log_dir)

print(f"Stock pool file: {manager.stock_pool_file}")
print(f"File exists: {os.path.exists(manager.stock_pool_file)}")

if os.path.exists(manager.stock_pool_file):
    with open(manager.stock_pool_file, 'r', encoding='utf-8') as f:
        import json
        data = json.load(f)
        print(f"Loaded data: {data}")
        print(f"Stocks from file: {data.get('stocks', [])}")
        print(f"Stocks count: {len(data.get('stocks', []))}")

print(f"Current pool size: {len(manager.current_pool)}")
print(f"Current pool: {manager.current_pool}")