#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

import baostock as bs
import pandas as pd
from datetime import datetime, timedelta

def analyze_stock(symbol):
    """分析股票是否符合牛回踩策略的买入条件"""
    print(f"正在分析股票: {symbol}")
    
    # 登录baostock
    lg = bs.login()
    if lg.error_code != '0':
        print(f"baostock登录失败: {lg.error_msg}")
        return
    
    print(f"baostock登录成功")
    
    # 获取最近365天的数据
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    rs = bs.query_history_k_data_plus(
        f"sh.{symbol}" if symbol.startswith('6') else f"sz.{symbol}",
        "date,code,open,high,low,close,volume",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="3"
    )
    
    if rs.error_code != '0':
        print(f"获取K线数据失败: {rs.error_msg}")
        bs.logout()
        return
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    print(f"获取到 {len(data_list)} 天数据")
    
    if len(data_list) < 200:
        print(f"数据量不足: {len(data_list)} 天，需要至少200天")
        bs.logout()
        return
    
    df = pd.DataFrame(data_list, columns=['date', 'code', 'open', 'high', 'low', 'close', 'volume'])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    
    # 获取最新价格
    current_price = float(df.iloc[-1]['close'])
    volume = float(df.iloc[-1]['volume'])
    
    # 计算均线
    ma20 = float(df['close'].tail(20).mean())
    ma250 = float(df['close'].tail(250).mean()) if len(df) >= 250 else float(df['close'].tail(len(df)).mean())
    v_ma5 = float(df['volume'].tail(5).mean())
    v_ma60 = float(df['volume'].tail(60).mean())
    
    print(f"\n股票 {symbol} 数据分析:")
    print(f"当前价格: {current_price}")
    print(f"MA20 (20日均线): {ma20}")
    print(f"MA250 (年线): {ma250}")
    print(f"当前成交量: {volume}")
    print(f"V_MA5 (5日均量): {v_ma5}")
    print(f"V_MA60 (60日均量): {v_ma60}")
    
    # 判断是否符合牛回踩策略的买入条件
    print(f"\n买入条件分析:")
    
    # 基础条件1: 股价 > 年线
    condition1 = current_price > ma250
    print(f"1. 股价 > 年线: {current_price} > {ma250} = {condition1}")
    
    # 基础条件2: 5日均量 > 60日均量
    condition2 = v_ma5 > v_ma60
    print(f"2. 5日均量 > 60日均量: {v_ma5} > {v_ma60} = {condition2}")
    
    # 信号条件1: 缩量（成交量 < 5日均量的80%）
    condition3 = volume < v_ma5 * 0.8
    print(f"3. 缩量（成交量 < 5日均量的80%）: {volume} < {v_ma5 * 0.8} = {condition3}")
    
    # 信号条件2: 回踩20线（收盘价在20日均线上下1.5%范围内）
    condition4 = abs(current_price / ma20 - 1) < 0.015
    price_diff = abs(current_price / ma20 - 1) * 100
    print(f"4. 回踩20线（收盘价在20日均线上下1.5%范围内）: {price_diff:.2f}% < 1.5% = {condition4}")
    
    base_condition = condition1 and condition2
    signal_condition = condition3 and condition4
    
    print(f"\n基础条件（股价 > 年线 AND 5日均量 > 60日均量）: {base_condition}")
    print(f"信号条件（缩量 AND 回踩20线）: {signal_condition}")
    print(f"\n是否满足买入条件: {base_condition and signal_condition}")
    
    if base_condition and signal_condition:
        price_range = f"{round(current_price * 0.98, 2)}-{round(current_price * 1.02, 2)}"
        stop_loss = round(current_price * 0.96, 2)
        print(f"\n建议价格区间: {price_range}")
        print(f"止损位: {stop_loss}")
    
    # 登出baostock
    bs.logout()

if __name__ == "__main__":
    symbol = "600170"  # 上海建工
    analyze_stock(symbol)