#!/usr/bin/env python3
import sys
import os

# 模拟app.py中的路径设置
LOG_DIR = "../logs"
print(f"LOG_DIR: {LOG_DIR}")
print(f"Absolute LOG_DIR: {os.path.abspath(LOG_DIR)}")
print(f"File exists: {os.path.exists(os.path.abspath(LOG_DIR))}")

stock_pool_file = os.path.join(LOG_DIR, "stock_pool.json")
print(f"Stock pool file: {stock_pool_file}")
print(f"Absolute stock pool file: {os.path.abspath(stock_pool_file)}")
print(f"File exists: {os.path.exists(os.path.abspath(stock_pool_file))}")