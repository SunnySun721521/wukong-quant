# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd

output = []

lg = bs.login()
output.append(f"login: {lg.error_code}")

symbol = "sz.002009"
rs = bs.query_history_k_data_plus(
    symbol, "date,open,high,low,close,volume",
    start_date="2018-01-01", end_date="2020-08-31",
    frequency="d", adjustflag="3"
)

data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())

output.append(f"data: {len(data_list)}")

df = pd.DataFrame(data_list, columns=['date','open','high','low','close','volume'])
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

for c in ['open','high','low','close','volume']:
    df[c] = pd.to_numeric(df[c])

df['ma20'] = df['close'].rolling(20).mean()
df['ma250'] = df['close'].rolling(250).mean()
df['v_ma5'] = df['volume'].rolling(5).mean()
df['v_ma60'] = df['volume'].rolling(60).mean()

tr1 = df['high'] - df['low']
tr2 = abs(df['high'] - df['close'].shift(1))
tr3 = abs(df['low'] - df['close'].shift(1))
tr = pd.concat([tr1,tr2,tr3], axis=1).max(axis=1)
df['atr'] = tr.rolling(20).mean()

d1 = pd.Timestamp('2020-08-03')
d2 = pd.Timestamp('2020-08-04')

for d, label in [(d1, "0803"), (d2, "0804")]:
    if d in df.index:
        r = df.loc[d]
        output.append(f"\n=== {label} ===")
        output.append(f"close={r['close']}, ma250={r['ma250']}")
        output.append(f"v_ma5={r['v_ma5']}, v_ma60={r['v_ma60']}")
        if pd.notna(r['ma250']):
            c1 = r['close'] > r['ma250']
            c2 = r['v_ma5'] > r['v_ma60']
            c3 = r['volume'] < r['v_ma5'] * 0.8
            c4 = abs(r['close']/r['ma20']-1) < 0.015
            output.append(f"c1={c1}, c2={c2}, c3={c3}, c4={c4}")
            output.append(f"BUY={c1 and c2 and c3 and c4}")

bs.logout()

with open("d:\\trae\\备份悟空52224\\out.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
