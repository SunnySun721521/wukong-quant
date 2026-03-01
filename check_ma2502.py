# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd

result = []

lg = bs.login()
result.append(f"login: {lg.error_code}")

symbol = "sz.002009"
start_date = "2019-01-01"
end_date = "2020-12-31"

rs = bs.query_history_k_data_plus(
    symbol,
    "date,close",
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
df['close'] = pd.to_numeric(df['close'])
df['ma250'] = df['close'].rolling(window=250).mean()

result.append(f"total: {len(df)} days")

first_ma250_date = None
for date, row in df.iterrows():
    if not pd.isna(row['ma250']):
        first_ma250_date = date
        result.append(f"first ma250: {date.date()}, value={row['ma250']:.2f}")
        break

result.append("=== 2020-06 onwards with ma250 ===")
for date, row in df.iterrows():
    if date >= pd.Timestamp('2020-06-01') and not pd.isna(row['ma250']):
        result.append(f"{date.date()}, close={row['close']:.2f}, ma250={row['ma250']:.2f}")

bs.logout()

with open("d:/trae/备份悟空52224/ma250_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(result))

print("done")
