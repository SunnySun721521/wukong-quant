#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

from strategy.stock_pool_manager import StockPoolManager

# 测试StockPoolManager的加载
LOG_DIR = "../logs"
manager = StockPoolManager(log_dir=LOG_DIR)

print(f"Stock pool file: {manager.stock_pool_file}")
print(f"File exists: {os.path.exists(manager.stock_pool_file)}")
print(f"Initial stocks: {manager.initial_stocks}")
print(f"Current pool size: {len(manager.current_pool)}")
print(f"Current pool: {manager.current_pool}")