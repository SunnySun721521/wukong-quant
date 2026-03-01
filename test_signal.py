# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd
import numpy as np

print("Step 1: Login to baostock")
lg = bs.login()
print(f"  Result: {lg.error_code}")

print("\nStep 2: Get stock data (002009)")
symbol = "sz.002009"
start_date = "2019-01-01"
end_date = "2025-12-31"

rs = bs.query_history_k_data_plus(
    symbol,
    "date,open,high,low,close,volume",
    start_date=start_date,
    end_date=end_date,
    frequency="d",
    adjustflag="3"
)

data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())

df = pd.DataFrame(data_list, columns=rs.fields)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

for col in ['open', 'high', 'low', 'close', 'volume']:
    df[col] = pd.to_numeric(df[col])

print(f"  Total records: {len(df)}")
print(f"  Date range: {df.index[0]} to {df.index[-1]}")

print("\nStep 3: Calculate indicators")
df['ma20'] = df['close'].rolling(window=20).mean()
df['ma250'] = df['close'].rolling(window=250).mean()
df['v_ma5'] = df['volume'].rolling(window=5).mean()
df['v_ma60'] = df['volume'].rolling(window=60).mean()

# ATR calculation
high = df['high']
low = df['low']
close = df['close']
tr1 = high - low
tr2 = abs(high - close.shift(1))
tr3 = abs(low - close.shift(1))
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
df['atr'] = tr.rolling(window=20).mean()

print(f"  Indicators calculated")

print("\nStep 4: Check 2020 data")
print("  Checking index positions for 2020:")
for i, date in enumerate(df.index):
    if date.year == 2020 and date.month in [1, 2, 3]:
        print(f"  i={i}, date={date.date()}, len(df)={len(df)}")
        if i >= 250:
            print(f"    This is where the loop starts (i >= 250)")
            break

print("\nStep 5: Simulate ATR strategy signal detection")
buy_signals = []
for i in range(250, len(df)):
    date = df.index[i]
    
    if pd.isna(df['atr'].iloc[i]) or pd.isna(df['ma250'].iloc[i]):
        continue
    
    close = df['close'].iloc[i]
    ma250 = df['ma250'].iloc[i]
    v_ma5 = df['v_ma5'].iloc[i]
    v_ma60 = df['v_ma60'].iloc[i]
    ma20 = df['ma20'].iloc[i]
    vol = df['volume'].iloc[i]
    
    buy_condition = (
        close > ma250 and
        v_ma5 > v_ma60 and
        vol < v_ma5 * 0.8 and
        abs(close / ma20 - 1) < 0.015
    )
    
    if buy_condition and date.year == 2020:
        buy_signals.append((date, close, ma250))
        print(f"  BUY SIGNAL: {date.date()}, close={close:.2f}, ma250={ma250:.2f}")

print(f"\nTotal 2020 buy signals: {len(buy_signals)}")

bs.logout()
print("\nDone!")
