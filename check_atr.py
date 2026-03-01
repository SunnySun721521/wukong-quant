# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd
import numpy as np

lg = bs.login()
print('baostock login:', lg.error_code, lg.error_msg)

symbol = "sz.002009"
end_date = "2020-12-31"
start_date = "2019-01-01"

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

df['ma20'] = df['close'].rolling(window=20).mean()
df['ma250'] = df['close'].rolling(window=250).mean()
df['v_ma5'] = df['volume'].rolling(window=5).mean()
df['v_ma60'] = df['volume'].rolling(window=60).mean()

# ATR计算
def calc_atr(df, period=20):
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

df['atr'] = calc_atr(df, 20)

print("\n=== 2020年3月-8月 ATR和ma250检查 ===")
print(f"{'日期':<12} {'收盘价':>8} {'ma250':>8} {'ATR':>8} {'ATR空?':>8} {'ma250空?':>10}")
print("-" * 60)

for date in df.index:
    if date >= pd.Timestamp('2020-03-01') and date <= pd.Timestamp('2020-08-31'):
        close = df.loc[date, 'close']
        ma250 = df.loc[date, 'ma250']
        atr = df.loc[date, 'atr']
        
        atr_na = "是" if pd.isna(atr) else "否"
        ma250_na = "是" if pd.isna(ma250) else "否"
        
        print(f"{str(date.date()):<12} {close:>8.2f} {ma250:>8.2f} {atr:>8.4f} {atr_na:>8} {ma250_na:>10}")

bs.logout()
