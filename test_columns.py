#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import efinance as ef
import pandas as pd

symbol = '600519'
start_date = '20240101'
end_date = '20250111'

print(f"测试股票: {symbol}")
print(f"日期范围: {start_date} 到 {end_date}")

try:
    start_date_str = start_date[:4] + '-' + start_date[4:6] + '-' + start_date[6:8]
    end_date_str = end_date[:4] + '-' + end_date[4:6] + '-' + end_date[6:8]
    
    print(f"转换后的日期: {start_date_str} 到 {end_date_str}")
    
    result = ef.stock.get_quote_history(
        stock_codes=[symbol], 
        beg=start_date_str, 
        end=end_date_str,
        klt=101
    )
    
    print(f"结果类型: {type(result)}")
    print(f"结果是否为None: {result is None}")
    
    if result is None or not result:
        print("结果为空或None")
    else:
        print(f"结果包含的股票: {list(result.keys())}")
        df = result.get(symbol)
        print(f"获取到的DataFrame类型: {type(df)}")
        print(f"DataFrame是否为None: {df is None}")
        
        if df is not None:
            print(f"DataFrame形状: {df.shape}")
            print(f"DataFrame列名: {df.columns.tolist()}")
            print(f"列名repr: {repr(df.columns.tolist())}")
            
            # 尝试不同的列名匹配方式
            print("\n尝试匹配列名:")
            for col in df.columns:
                print(f"  '{col}' (长度: {len(col)}, repr: {repr(col)})")
            
            # 尝试使用实际的列名
            try:
                df_clean = df[['股票代码', '股票名称', '日期', '开盘', '收盘', '最高', '最低', '成交量']].copy()
                print(f"\n使用标准列名选择成功！形状: {df_clean.shape}")
            except KeyError as e:
                print(f"\n使用标准列名选择失败: {e}")
                
                # 尝试使用带空格的列名
                try:
                    df_clean = df[['股票代码', '股票名称', '日期', ' 开盘', '收盘', '最高', '最 低', '成交 量']].copy()
                    print(f"使用带空格列名选择成功！形状: {df_clean.shape}")
                except KeyError as e2:
                    print(f"使用带空格列名选择失败: {e2}")
except Exception as e:
    print(f"发生异常: {e}")
    import traceback
    traceback.print_exc()