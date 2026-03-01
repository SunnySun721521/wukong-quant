# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd

output = []

lg = bs.login()
output.append(f"baostock login: {lg.error_code}")

symbol = "sz.002009"
end_date = "2020-08-31"
start_date = "2020-01-01"

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

# ATR
high = df['high']
low = df['low']
close = df['close']
tr1 = high - low
tr2 = abs(high - close.shift(1))
tr3 = abs(low - close.shift(1))
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
df['atr'] = tr.rolling(window=20).mean()

output.append("\n=== 2020年7月下旬 - 8月上旬 ===")
output.append("日期         收盘    ma250    v_ma5     v_ma60")

for date in df.index:
    if date >= pd.Timestamp('2020-07-20') and date <= pd.Timestamp('2020-08-10'):
        close_v = df.loc[date, 'close']
        ma250 = df.loc[date, 'ma250']
        v_ma5 = df.loc[date, 'v_ma5']
        v_ma60 = df.loc[date, 'v_ma60']
        output.append(f"{str(date.date())}  {close_v:>6.2f}  {ma250:>6.2f}  {v_ma5:>8.0f}  {v_ma60:>8.0f}")

output.append("\n=== 买入信号 ===")
for i in range(250, len(df)):
    date = df.index[i]
    
    if pd.isna(df['atr'].iloc[i]) or pd.isna(df['ma250'].iloc[i]):
        continue
    
    close_v = df['close'].iloc[i]
    ma250 = df['ma250'].iloc[i]
    v_ma5 = df['v_ma5'].iloc[i]
    v_ma60 = df['v_ma60'].iloc[i]
    ma20 = df['ma20'].iloc[i]
    vol = df['volume'].iloc[i]
    
    buy = close_v > ma250 and v_ma5 > v_ma60 and vol < v_ma5 * 0.8 and abs(close_v / ma20 - 1) < 0.015
    
    if buy:
        output.append(f"{date.date()} 买入! close={close_v:.2f} ma250={ma250:.2f} v_ma5={v_ma5:.0f} v_ma60={v_ma60:.0f}")

output.append("\n=== 卖出信号(跌破ma250) ===")
for i in range(251, len(df)):
    date = df.index[i]
    prev_date = df.index[i-1]
    
    close_v = df['close'].iloc[i]
    ma250 = df['ma250'].iloc[i]
    prev_close = df['close'].iloc[i-1]
    prev_ma250 = df['ma250'].iloc[i-1]
    
    if prev_close > prev_ma250 and close_v < ma250:
        output.append(f"{date.date()} 卖出! close={close_v:.2f} ma250={ma250:.2f}")

bs.logout()

with open("d:/trae/备份悟空52224/aug_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("Done")
