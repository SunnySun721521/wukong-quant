#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import efinance as ef
from datetime import datetime

def test_efinance():
    symbol = "000001"
    start_date = "20230101"
    end_date = datetime.now().strftime("%Y%m%d")
    
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
    
    if symbol in result:
        df = result[symbol]
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        print(f"First few rows: {df.head()}")
        print(f"Data types: {df.dtypes}")
    else:
        print(f"Symbol {symbol} not in result")
        # 查看第一个键值对
        if result:
            first_key = list(result.keys())[0]
            df = result[first_key]
            print(f"First key: {first_key}")
            print(f"DataFrame shape: {df.shape}")
            print(f"DataFrame columns: {df.columns.tolist()}")
            print(f"First few rows: {df.head()}")

if __name__ == "__main__":
    test_efinance()