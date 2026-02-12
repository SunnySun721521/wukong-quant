#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
from strategy.data_provider import DataProvider

symbol = '600519'
start_date = '20240101'
end_date = '20250111'

print(f"测试股票: {symbol}")
print(f"日期范围: {start_date} 到 {end_date}")

try:
    df = DataProvider.get_kline_data(symbol, start_date, end_date)
    if df is not None:
        print(f"  数据获取成功！")
        print(f"  数据形状: {df.shape}")
        print(f"  数据列: {df.columns.tolist()}")
        print(f"  前3行:")
        print(df.head(3))
    else:
        print(f"  数据获取失败！")
except Exception as e:
    print(f"  发生异常: {e}")
    import traceback
    traceback.print_exc()