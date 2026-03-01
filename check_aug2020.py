# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd

lg = bs.login()
print('baostock login:', lg.error_code)

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

# ATR calculation
high = df['high']
low = df['low']
close = df['close']
tr1 = high - low
tr2 = abs(high - close.shift(1))
tr3 = abs(low - close.shift(1))
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
df['atr'] = tr.rolling(window=20).mean()

print("\n=== 2020年7月下旬 - 8月上旬数据 ===")
print(f"{'日期':<12} {'收盘':>8} {'ma250':>8} {'v_ma5':>12} {'v_ma60':>12} {'ATR':>8}")
print("-" * 65)

for date in df.index:
    if date >= pd.Timestamp('2020-07-20') and date <= pd.Timestamp('2020-08-10'):
        close = df.loc[date, 'close']
        ma250 = df.loc[date, 'ma250']
        v_ma5 = df.loc[date, 'v_ma5']
        v_ma60 = df.loc[date, 'v_ma60']
        atr = df.loc[date, 'atr']
        
        print(f"{str(date.date()):<12} {close:>8.2f} {ma250:>8.2f} {v_ma5:>12.0f} {v_ma60:>12.0f} {atr:>8.2f}")

print("\n=== 买入/卖出信号检测 ===")
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
    atr = df['atr'].iloc[i]
    
    # 买入条件
    buy = close > ma250 and v_ma5 > v_ma60 and vol < v_ma5 * 0.8 and abs(close / ma20 - 1) < 0.015
    
    if buy:
        print(f"{date.date()} 买入! close={close:.2f} ma250={ma250:.2f} v_ma5={v_ma5:.0f} v_ma60={v_ma60:.0f}")
    
    # 卖出条件：收盘价跌破ma250
    if close < ma250 and i > 0:
        prev_close = df['close'].iloc[i-1]
        prev_ma250 = df['ma250'].iloc[i-1]
        if prev_close > prev_ma250:
            print(f"{date.date()} 卖出(跌破年线)! close={close:.2f} ma250={ma250:.2f}")

bs.logout()
