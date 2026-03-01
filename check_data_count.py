# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd

lg = bs.login()
print(f"login: {lg.error_code}")

# 测试从2018-01-01到2020-08-03的数据量
symbol = "sz.002009"
start_date = "2018-01-01"
end_date = "2020-08-03"

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

print(f"从{start_date}到{end_date}的数据量: {len(data_list)}条")

# 看看2019年有多少数据
rs2 = bs.query_history_k_data_plus(
    symbol,
    "date,close",
    start_date="2019-01-01",
    end_date="2019-12-31",
    frequency="d",
    adjustflag="3"
)

data_list2 = []
while (rs2.error_code == '0') & rs2.next():
    data_list2.append(rs2.get_row_data())

print(f"2019年数据量: {len(data_list2)}条")

bs.logout()
