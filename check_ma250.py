# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd

lg = bs.login()

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

print(f"总共 {len(df)} 个交易日")
print("\n=== 2019年数据量 ===")
df_2019 = df[df.index.year == 2019]
print(f"2019年交易日数: {len(df_2019)}")

print("\n=== 首次有ma250数据的日期 ===")
for date, row in df.iterrows():
    if not pd.isna(row['ma250']):
        print(f"{date.date()} - ma250={row['ma250']:.2f}, 之前有{len(df[df.index < date])}个交易日")
        break

print("\n=== 2020年有ma250后的数据 ===")
print("日期         收盘    ma250")
for date, row in df.iterrows():
    if date >= pd.Timestamp('2020-06-01') and not pd.isna(row['ma250']):
        print(f"{date.date()}  {row['close']:>6.2f}  {row['ma250']:>6.2f}")

bs.logout()
