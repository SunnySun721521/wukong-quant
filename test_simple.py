#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import efinance as ef
import pandas as pd

symbol = '600519'
start_date = '20240101'
end_date = '20250111'

print(f"测试股票: {symbol}")
print(f"日期范围: {start_date} 到 {end_date}")

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
        
        # 清理列名中的空格
        df.columns = df.columns.str.replace(' ', '')
        print(f"清理后的列名: {df.columns.tolist()}")
        
        df_clean = df[['股票代码', '股票名称', '日期', '开盘', '收盘', '最高', '最低', '成交量']].copy()
        print(f"选择列后的形状: {df_clean.shape}")
        
        df_clean.rename(columns={
            "日期": "datetime",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume"
        }, inplace=True)
        
        print(f"重命名后的列名: {df_clean.columns.tolist()}")
        
        df_clean["datetime"] = pd.to_datetime(df_clean["datetime"])
        df_clean.set_index("datetime", inplace=True)
        
        print(f"最终DataFrame形状: {df_clean.shape}")
        print(f"最终DataFrame索引: {df_clean.index.name}")
        print("数据处理成功！")
    else:
        print("DataFrame为空或None")