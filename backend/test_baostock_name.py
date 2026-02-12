#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import baostock as bs

print("=== 测试baostock获取股票003816的名称 ===")

lg = bs.login()
print(f"登录结果: {lg.error_code}, {lg.error_msg}")

if lg.error_code == '0':
    # 转换股票代码为baostock格式
    symbol = "003816"
    bs_symbol = f"sz.{symbol}" if symbol.startswith('0') else f"sh.{symbol}"
    print(f"baostock代码: {bs_symbol}")
    
    # 获取股票信息
    rs = bs.query_stock_basic(code=bs_symbol)
    print(f"查询结果: {rs.error_code}, {rs.error_msg}")
    
    if rs.error_code == '0':
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        if data_list:
            print(f"获取到股票信息:")
            for row in data_list:
                print(f"  代码: {row[0]}, 名称: {row[1]}, 行业: {row[2]}")
        else:
            print("未获取到股票信息")
    else:
        print(f"查询失败: {rs.error_msg}")
    
    bs.logout()
else:
    print("登录失败")

print("\n=== 测试完成 ===")