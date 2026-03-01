#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import akshare as ak
from datetime import datetime

def test_akshare():
    symbol = "000001"
    start_date = "2023-01-01"
    end_date = "2024-01-01"
    
    print(f"Testing akshare for symbol: {symbol}")
    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")
    
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust="qfq"
    )
    
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {df.columns.tolist()}")
    print(f"First few rows: {df.head()}")
    print(f"Data types: {df.dtypes}")
    
    # 测试选择列
    try:
        df_selected = df[["日期", "开盘", "收盘", "最高", "最低", "成交量"]].copy()
        print(f"\nSelected columns shape: {df_selected.shape}")
        print(f"Selected columns: {df_selected.columns.tolist()}")
        print(f"Selected columns first few rows: {df_selected.head()}")
    except Exception as e:
        print(f"\nError selecting columns: {e}")

if __name__ == "__main__":
    test_akshare()