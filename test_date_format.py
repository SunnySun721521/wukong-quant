#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import efinance as ef
import pandas as pd

symbol = '600519'

# 尝试不同的日期格式
test_dates = [
    ('2024-01-01', '2025-01-11'),
    ('20240101', '20250111'),
]

for start_date, end_date in test_dates:
    print(f"\n测试日期格式: {start_date} 到 {end_date}")
    
    try:
        result = ef.stock.get_quote_history(
            stock_codes=[symbol], 
            beg=start_date, 
            end=end_date,
            klt=101
        )
        
        if result and symbol in result:
            df = result[symbol]
            print(f"  数据形状: {df.shape}")
            print(f"  数据列: {df.columns.tolist()}")
            if not df.empty:
                print(f"  前3行:")
                print(df.head(3))
                break
            else:
                print("  数据为空")
        else:
            print("  结果为空")
    except Exception as e:
        print(f"  异常: {e}")