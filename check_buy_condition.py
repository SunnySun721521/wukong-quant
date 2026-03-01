# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd
from datetime import datetime, timedelta

lg = bs.login()
print('baostock login:', lg.error_code, lg.error_msg)

symbol = "sz.002009"
end_date = "2020-08-10"
start_date = "2020-06-01"

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

print("\n=== 2020年7月25日 - 8月10日 数据分析 ===")
print(f"{'日期':<12} {'收盘价':>8} {'ma250':>8} {'站上年线':>6} {'v_ma5':>10} {'v_ma60':>10} {'量放大':>5} {'缩量':>5} {'ma20':>8} {'回踩':>6}")
print("-" * 95)

for date in df.index:
    if date >= pd.Timestamp('2020-07-25'):
        close = df.loc[date, 'close']
        ma250 = df.loc[date, 'ma250']
        v_ma5 = df.loc[date, 'v_ma5']
        v_ma60 = df.loc[date, 'v_ma60']
        ma20 = df.loc[date, 'ma20']
        
        above_ma250 = "是" if (pd.notna(ma250) and close > ma250) else "否"
        vol放大 = "是" if (pd.notna(v_ma5) and pd.notna(v_ma60) and v_ma5 > v_ma60) else "否"
        vol缩量 = "是" if (pd.notna(v_ma5) and df.loc[date, 'volume'] < v_ma5 * 0.8) else "否"
        回踩 = "是" if (pd.notna(ma20) and abs(close / ma20 - 1) < 0.015) else "否"
        
        print(f"{str(date.date()):<12} {close:>8.2f} {ma250:>8.2f} {above_ma250:>6} {v_ma5:>10.0f} {v_ma60:>10.0f} {vol放大:>5} {vol缩量:>5} {ma20:>8.2f} {回踩:>6}")

bs.logout()
