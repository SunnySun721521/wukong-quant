# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

from strategy.backtest_engine import BacktestEngine

lg = bs.login()
print('baostock login:', lg.error_code)

engine = BacktestEngine()

symbol = "002009"
start_date = "20200101"
end_date = "20251231"

stock_start = "20190101"

print(f"\n获取股票数据: {symbol} 从 {stock_start} 到 {end_date}")

df = None
import sys
for part in sys.path:
    if os.path.exists(os.path.join(part, 'strategy', 'data_provider.py')):
        from strategy.data_provider import DataProvider
        df = DataProvider.get_kline_data(symbol, stock_start, end_date)
        break

if df is not None:
    print(f"获取数据成功: {len(df)} 条")
    print(f"数据范围: {df.index[0]} 到 {df.index[-1]}")
    
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma250'] = df['close'].rolling(window=250).mean()
    df['v_ma5'] = df['volume'].rolling(window=5).mean()
    df['v_ma60'] = df['volume'].rolling(window=60).mean()
    
    print("\n检查2020年数据:")
    for date in df.index:
        if date.year == 2020 and date.month in [3, 7, 12]:
            close = df.loc[date, 'close']
            ma250 = df.loc[date, 'ma250']
            v_ma5 = df.loc[date, 'v_ma5']
            v_ma60 = df.loc[date, 'v_ma60']
            ma20 = df.loc[date, 'ma20']
            vol = df.loc[date, 'volume']
            
            if pd.notna(ma250) and pd.notna(v_ma5) and pd.notna(v_ma60) and pd.notna(ma20):
                cond1 = close > ma250
                cond2 = v_ma5 > v_ma60
                cond3 = vol < v_ma5 * 0.8
                cond4 = abs(close / ma20 - 1) < 0.015
                
                buy = "✓买入" if (cond1 and cond2 and cond3 and cond4) else ""
                print(f"{date.date()} close={close:.2f} ma250={ma250:.2f} {cond1} v_ma5={v_ma5:.0f} v_ma60={v_ma60:.0f} {cond2} vol={vol:.0f} {cond3} ma20={ma20:.2f} {cond4} {buy}")

bs.logout()
