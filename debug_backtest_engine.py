#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试回测引擎的数据准备逻辑
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategy.backtest_engine import BacktestEngine
from strategy.data_provider import DataProvider

def debug_prepare_data():
    """调试数据准备逻辑"""
    print("=== 调试回测引擎数据准备 ===")
    
    # 初始化回测引擎
    engine = BacktestEngine()
    
    # 测试参数
    symbols = ['002371', '300274']
    start_date = '20230101'
    end_date = '20260123'
    
    for symbol in symbols:
        print(f"\n测试股票: {symbol}")
        
        # 测试直接使用DataProvider获取
        print("1. 直接使用DataProvider获取:")
        df1 = DataProvider.get_kline_data(symbol, start_date, end_date)
        if df1 is not None and not df1.empty:
            print(f"✓ 成功，共 {len(df1)} 条记录")
            print(f"列: {list(df1.columns)}")
        else:
            print("✗ 失败")
        
        # 测试使用BacktestEngine.prepare_data获取
        print("2. 使用BacktestEngine.prepare_data获取:")
        df2 = engine.prepare_data(symbol, start_date, end_date)
        if df2 is not None and not df2.empty:
            print(f"✓ 成功，共 {len(df2)} 条记录")
            print(f"列: {list(df2.columns)}")
        else:
            print("✗ 失败")
        
        # 检查数据类型
        if df1 is not None:
            print("3. 数据类型检查:")
            print(f"DataFrame类型: {type(df1)}")
            print(f"索引类型: {type(df1.index)}")
            print(f"数值列类型:")
            for col in df1.columns:
                print(f"  {col}: {df1[col].dtype}")

if __name__ == "__main__":
    debug_prepare_data()
