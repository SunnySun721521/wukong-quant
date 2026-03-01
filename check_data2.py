# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd
import os

output = []
output.append("Starting...")

try:
    lg = bs.login()
    output.append(f"login: {lg.error_code}")
    
    symbol = "sz.002009"
    
    # Test 1: 2018-01-01 to 2020-08-03
    rs = bs.query_history_k_data_plus(
        symbol, "date,close",
        start_date="2018-01-01",
        end_date="2020-08-03",
        frequency="d", adjustflag="3"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    output.append(f"2018-01-01 to 2020-08-03: {len(data_list)} days")
    
    # Test 2: 2019 full year
    rs2 = bs.query_history_k_data_plus(
        symbol, "date,close",
        start_date="2019-01-01",
        end_date="2019-12-31",
        frequency="d", adjustflag="3"
    )
    
    data_list2 = []
    while (rs2.error_code == '0') & rs2.next():
        data_list2.append(rs2.get_row_data())
    
    output.append(f"2019 year: {len(data_list2)} days")
    
    # Test 3: When does data start
    rs3 = bs.query_history_k_data_plus(
        symbol, "date,close",
        start_date="2015-01-01",
        end_date="2020-12-31",
        frequency="d", adjustflag="3"
    )
    
    data_list3 = []
    while (rs3.error_code == '0') & rs3.next():
        data_list3.append(rs3.get_row_data())
    
    if data_list3:
        first_date = data_list3[0][0]
        last_date = data_list3[-1][0]
        output.append(f"First date: {first_date}, Last date: {last_date}, Total: {len(data_list3)}")
    
    bs.logout()
    output.append("Done")
    
except Exception as e:
    output.append(f"Error: {e}")

# Write to file
with open("d:/trae/备份悟空52224/result_data.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("Done - check result_data.txt")
