#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import efinance as ef
from datetime import datetime

def test_efinance_detail():
    symbol = "600519"
    start_date = "20230101"
    end_date = "20240101"
    
    print(f"Testing efinance for symbol: {symbol}")
    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")
    
    result = ef.stock.get_quote_history(
        stock_codes=[symbol],
        beg=start_date,
        end=end_date,
        klt=101
    )
    
    print(f"Result type: {type(result)}")
    print(f"Result keys: {list(result.keys())}")
    print(f"Result keys types: {[type(key) for key in result.keys()]}")
    
    for key in result.keys():
        print(f"\nProcessing key: {key} (type: {type(key)})")
        df = result[key]
        print(f"DataFrame type: {type(df)}")
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        print(f"DataFrame columns types: {[type(col) for col in df.columns]}")
        
        # 清理列名中的空格
        df.columns = df.columns.str.replace(' ', '')
        print(f"Cleaned columns: {df.columns.tolist()}")
        
        # 检查是否包含股票名称列
        if '股票名称' in df.columns:
            print(f"股票名称列数据类型: {df['股票名称'].dtype}")
            print(f"股票名称列前5个值: {df['股票名称'].head().tolist()}")
        
        # 选择需要的列
        if all(col in df.columns for col in ['日期', '开盘', '收盘', '最高', '最低', '成交量']):
            df_selected = df[['日期', '开盘', '收盘', '最高', '最低', '成交量']].copy()
            print(f"Selected columns shape: {df_selected.shape}")
            print(f"Selected columns: {df_selected.columns.tolist()}")
            print(f"Selected columns dtypes: {df_selected.dtypes}")
            
            # 转换日期列
            df_selected["datetime"] = pd.to_datetime(df_selected["日期"])
            df_selected.set_index("datetime", inplace=True)
            
            # 确保数值列是数值类型
            numeric_cols = ['开盘', '收盘', '最高', '最低', '成交量']
            for col in numeric_cols:
                df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')
            
            print(f"Final DataFrame shape: {df_selected.shape}")
            print(f"Final DataFrame columns: {df_selected.columns.tolist()}")
            print(f"Final DataFrame dtypes: {df_selected.dtypes}")
            print(f"Final DataFrame first few rows: {df_selected.head()}")
        else:
            print("Required columns not found")

if __name__ == "__main__":
    test_efinance_detail()