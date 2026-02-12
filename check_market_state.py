#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查市场状态判断逻辑
"""

import os
import sys
from datetime import datetime

# 添加策略目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategy'))

from data_provider import DataProvider
import pandas as pd


def check_hs300_data():
    """检查沪深300指数数据"""
    print("=== 检查沪深300指数数据 ===")
    
    # 从本地文件加载数据
    df = DataProvider.load_hs300_data()
    
    if df is not None and not df.empty:
        print(f"数据行数: {len(df)}")
        print(f"数据时间范围: {df.index.min()} 到 {df.index.max()}")
        print(f"列名: {list(df.columns)}")
        
        # 检查最近几天的数据
        recent_data = df.tail(10)
        print("\n最近10天的数据:")
        print(recent_data[['close', 'ma120']])
        
        # 计算最近几天的市场状态
        print("\n最近10天的市场状态:")
        for date, row in recent_data.iterrows():
            if not pd.isna(row['ma120']):
                if row['close'] > row['ma120']:
                    market_state = '牛'
                else:
                    market_state = '熊'
            else:
                market_state = '熊'
            print(f"{date.date()}: 收盘价={row['close']:.2f}, MA120={row['ma120']:.2f}, 市场状态={market_state}")
        
        return df
    else:
        print("无法加载沪深300指数数据")
        return None


def check_data_quality(df):
    """检查数据质量"""
    if df is None or df.empty:
        return
    
    print("\n=== 检查数据质量 ===")
    
    # 检查是否有NaN值
    nan_count = df.isna().sum()
    print("NaN值统计:")
    print(nan_count)
    
    # 检查ma120的计算
    print("\n=== 检查MA120计算 ===")
    # 重新计算ma120并与现有值比较
    df['ma120_calc'] = df['close'].rolling(window=120).mean()
    # 检查最近几天的差异
    recent_data = df.tail(10)
    print("最近10天的MA120值比较:")
    print(recent_data[['close', 'ma120', 'ma120_calc']])
    
    # 计算差异
    diff = recent_data['ma120'] - recent_data['ma120_calc']
    print("\nMA120差异:")
    print(diff)


if __name__ == "__main__":
    print("开始检查市场状态判断逻辑")
    
    # 检查沪深300指数数据
    df = check_hs300_data()
    
    # 检查数据质量
    if df is not None and not df.empty:
        check_data_quality(df)
    
    print("检查完成")
