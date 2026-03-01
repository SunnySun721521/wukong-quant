#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试数据提供者的K线数据获取功能
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategy.data_provider import DataProvider

def test_kline_data():
    """测试K线数据获取"""
    print("=== 测试K线数据获取 ===")
    
    # 测试参数
    symbols = ['002371', '300274']
    start_date = '20230101'
    end_date = '20260123'
    
    for symbol in symbols:
        print(f"\n测试股票: {symbol}")
        print(f"时间范围: {start_date} 到 {end_date}")
        
        # 测试获取K线数据
        df = DataProvider.get_kline_data(symbol, start_date, end_date)
        
        if df is not None and not df.empty:
            print(f"✓ 成功获取数据，共 {len(df)} 条记录")
            print(f"数据列: {list(df.columns)}")
            print(f"数据范围: {df.index.min()} 到 {df.index.max()}")
            print("前5条数据:")
            print(df.head())
        else:
            print("✗ 无法获取数据")
            
            # 尝试直接使用efinance获取
            try:
                import efinance as ef
                print("\n尝试直接使用efinance获取:")
                result = ef.stock.get_quote_history(
                    stock_codes=[symbol], 
                    beg=start_date, 
                    end=end_date,
                    klt=101
                )
                
                if result is not None:
                    print(f"efinance返回结果类型: {type(result)}")
                    print(f"efinance返回结果长度: {len(result)}")
                    
                    if isinstance(result, dict):
                        for key, value in result.items():
                            print(f"Key: {key}, Value type: {type(value)}")
                            if hasattr(value, 'shape'):
                                print(f"DataFrame shape: {value.shape}")
                            if hasattr(value, 'columns'):
                                print(f"Columns: {list(value.columns)}")
            except Exception as e:
                print(f"efinance测试失败: {e}")

if __name__ == "__main__":
    test_kline_data()
