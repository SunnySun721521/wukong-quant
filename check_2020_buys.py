# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd

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

print("\n=== 2020年满足买入条件的日期 ===")
buy_count = 0
for date in df.index:
    if date >= pd.Timestamp('2020-01-01'):
        close = df.loc[date, 'close']
        ma250 = df.loc[date, 'ma250']
        v_ma5 = df.loc[date, 'v_ma5']
        v_ma60 = df.loc[date, 'v_ma60']
        ma20 = df.loc[date, 'ma20']
        volume = df.loc[date, 'volume']
        
        if pd.notna(ma250) and pd.notna(v_ma5) and pd.notna(v_ma60) and pd.notna(ma20):
            cond1 = close > ma250
            cond2 = v_ma5 > v_ma60
            cond3 = volume < v_ma5 * 0.8
            cond4 = abs(close / ma20 - 1) < 0.015
            
            if cond1 and cond2 and cond3 and cond4:
                buy_count += 1
                print(f"{date.date()} 买入! 收盘={close:.2f} ma250={ma250:.2f} v_ma5={v_ma5:.0f} v_ma60={v_ma60:.0f} vol={volume:.0f} ma20={ma20:.2f}")

print(f"\n2020年满足买入条件的天数: {buy_count}")

bs.logout()
