# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd
import sys

lg = bs.login()
print('login success')

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
high = df['high']
low = df['low']
close = df['close']
tr1 = high - low
tr2 = abs(high - close.shift(1))
tr3 = abs(low - close.shift(1))
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
df['atr'] = tr.rolling(window=20).mean()

output = []
output.append("=== 2020年3月-8月 ATR和ma250检查 ===")
output.append("日期        收盘价    ma250     ATR     ATR空?   ma250空?")
output.append("-" * 60)

for date in df.index:
    if date >= pd.Timestamp('2020-03-01') and date <= pd.Timestamp('2020-08-31'):
        close_val = df.loc[date, 'close']
        ma250 = df.loc[date, 'ma250']
        atr = df.loc[date, 'atr']
        
        atr_na = "是" if pd.isna(atr) else "否"
        ma250_na = "是" if pd.isna(ma250) else "否"
        
        output.append(f"{str(date.date())} {close_val:>8.2f} {ma250:>8.2f} {atr:>8.4f} {atr_na:>8} {ma250_na:>10}")

result = "\n".join(output)

with open("d:/trae/备份悟空52224/atr_check_result.txt", "w", encoding="utf-8") as f:
    f.write(result)

print("Done")
bs.logout()
