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
        
        if df is not None and not df.empty:
            print(f"DataFrame形状: {df.shape}")
            print(f"DataFrame列名: {df.columns.tolist()}")
            
            df = df[['股票代码', '股票名称', '日期', '开盘', '收盘', '最高', '最低', '成交量']].copy()
            print(f"选择列后的形状: {df.shape}")
            
            df.rename(columns={
                "日期": "datetime",
                "开盘": "open",
                "最高": "high",
                "最低": "low",
                "收盘": "close",
                "成交量": "volume"
            }, inplace=True)
            
            print(f"重命名后的列名: {df.columns.tolist()}")
            
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)
            
            print(f"最终DataFrame形状: {df.shape}")
            print(f"最终DataFrame索引: {df.index.name}")
            print("数据处理成功！")
        else:
            print(f"DataFrame为空或None，df.empty={df.empty}")
            if df is not None:
                print(f"DataFrame实际形状: {df.shape}")
                print(f"DataFrame实际列名: {df.columns.tolist()}")
                print(f"DataFrame前5行:")
                print(df.head())
except Exception as e:
    print(f"发生异常: {e}")
    import traceback
    traceback.print_exc()