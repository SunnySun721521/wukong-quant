#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试沪深300指数数据下载和市场状态判断
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 添加策略目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategy'))

from data_provider import DataProvider
from backtest_engine import BaseStrategy


def test_hs300_data_download():
    """测试下载沪深300指数数据"""
    print("=== 测试下载沪深300指数数据 ===")
    
    # 下载数据
    df = DataProvider.download_hs300_data()
    
    if df is not None and not df.empty:
        print(f"下载成功，数据行数: {len(df)}")
        print(f"数据时间范围: {df.index.min()} 到 {df.index.max()}")
        print(f"列名: {list(df.columns)}")
        
        # 保存到本地文件
        file_path = DataProvider.save_hs300_data(df)
        if file_path:
            print(f"保存成功，文件路径: {file_path}")
        else:
            print("保存失败")
        
        return True
    else:
        print("下载失败")
        return False


def test_hs300_data_load():
    """测试从本地文件加载沪深300指数数据"""
    print("\n=== 测试从本地文件加载沪深300指数数据 ===")
    
    # 从本地文件加载数据
    df = DataProvider.load_hs300_data()
    
    if df is not None and not df.empty:
        print(f"加载成功，数据行数: {len(df)}")
        print(f"数据时间范围: {df.index.min()} 到 {df.index.max()}")
        print(f"列名: {list(df.columns)}")
        
        # 检查是否有ma120列
        if 'ma120' in df.columns:
            print("数据包含120日移动平均线")
        else:
            print("数据不包含120日移动平均线")
        
        return True
    else:
        print("加载失败")
        return False


def test_hs300_data_update():
    """测试更新沪深300指数数据"""
    print("\n=== 测试更新沪深300指数数据 ===")
    
    # 更新数据
    success = DataProvider.update_hs300_data()
    
    if success:
        print("更新成功")
        return True
    else:
        print("更新失败")
        return False


def test_market_state_judgment():
    """测试市场状态判断"""
    print("\n=== 测试市场状态判断 ===")
    
    # 初始化BaseStrategy类的沪深300数据
    BaseStrategy._initialize_hs300_data()
    
    if BaseStrategy.hs300_df is not None and not BaseStrategy.hs300_df.empty:
        print("沪深300数据初始化成功")
        
        # 测试最近几天的市场状态
        recent_dates = BaseStrategy.hs300_df.index.sort_values()[-5:]
        
        for date in recent_dates:
            # 直接使用BaseStrategy中的市场状态判断逻辑
            market_state = '熊'  # 默认熊市
            
            try:
                # 查找当前日期的沪深300指数数据
                if date in BaseStrategy.hs300_df.index:
                    row = BaseStrategy.hs300_df.loc[date]
                    if not pd.isna(row['ma120']):
                        # 当沪深300指数价格在120日移动平均线之上时为牛市，之下时为熊市
                        if row['close'] > row['ma120']:
                            market_state = '牛'
                        else:
                            market_state = '熊'
                    else:
                        # 移动平均线数据不足时保持默认状态
                        market_state = '熊'
                else:
                    # 没有当前日期的数据时，尝试查找最接近的日期
                    closest_date = BaseStrategy.hs300_df.index.get_loc(date, method='nearest')
                    row = BaseStrategy.hs300_df.iloc[closest_date]
                    if not pd.isna(row['ma120']):
                        if row['close'] > row['ma120']:
                            market_state = '牛'
                        else:
                            market_state = '熊'
                    else:
                        market_state = '熊'
            except Exception as e:
                print(f"计算市场状态失败: {e}")
                # 失败时保持默认状态
                market_state = '熊'
            
            print(f"日期: {date.date()}, 市场状态: {market_state}")
        
        return True
    else:
        print("沪深300数据初始化失败")
        return False


if __name__ == "__main__":
    print("开始测试沪深300指数数据功能")
    
    # 运行测试
    test1 = test_hs300_data_download()
    test2 = test_hs300_data_load()
    test3 = test_hs300_data_update()
    test4 = test_market_state_judgment()
    
    print("\n=== 测试结果 ===")
    print(f"下载测试: {'通过' if test1 else '失败'}")
    print(f"加载测试: {'通过' if test2 else '失败'}")
    print(f"更新测试: {'通过' if test3 else '失败'}")
    print(f"市场状态判断测试: {'通过' if test4 else '失败'}")
    
    if all([test1, test2, test3, test4]):
        print("所有测试通过！")
    else:
        print("部分测试失败，请检查原因。")
