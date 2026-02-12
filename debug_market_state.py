#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试市场状态判断逻辑
"""

import os
import sys
from datetime import datetime, date
import pandas as pd

# 添加策略目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategy'))

from data_provider import DataProvider
from backtest_engine import BaseStrategy


def debug_hs300_data_initialization():
    """调试沪深300指数数据初始化"""
    print("=== 调试沪深300指数数据初始化 ===")
    
    # 检查数据文件是否存在
    data_dir = os.path.join(os.path.dirname(__file__), 'strategy', 'data')
    file_path = os.path.join(data_dir, 'hs300_data.csv')
    print(f"数据文件路径: {file_path}")
    print(f"数据文件是否存在: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        print(f"数据文件大小: {file_size} bytes")
        
        # 读取文件内容
        try:
            df = pd.read_csv(file_path, nrows=10)
            print("\n文件前10行:")
            print(df)
        except Exception as e:
            print(f"读取文件失败: {e}")
    
    # 初始化BaseStrategy类的沪深300数据
    print("\n初始化BaseStrategy.hs300_df...")
    BaseStrategy._initialize_hs300_data()
    
    print(f"\nBaseStrategy.hs300_df是否为None: {BaseStrategy.hs300_df is None}")
    if BaseStrategy.hs300_df is not None:
        print(f"数据行数: {len(BaseStrategy.hs300_df)}")
        print(f"索引类型: {type(BaseStrategy.hs300_df.index[0])}")
        print(f"索引范围: {BaseStrategy.hs300_df.index.min()} 到 {BaseStrategy.hs300_df.index.max()}")
        print(f"列名: {list(BaseStrategy.hs300_df.columns)}")
        
        # 检查是否包含ma120列
        if 'ma120' in BaseStrategy.hs300_df.columns:
            print("包含ma120列")
            # 检查ma120是否有值
            ma120_notna = BaseStrategy.hs300_df['ma120'].notna().sum()
            print(f"ma120非空值数量: {ma120_notna}")
            print(f"ma120空值数量: {len(BaseStrategy.hs300_df) - ma120_notna}")
        else:
            print("不包含ma120列")
    
    return BaseStrategy.hs300_df is not None


def debug_market_state_judgment():
    """调试市场状态判断逻辑"""
    print("\n=== 调试市场状态判断逻辑 ===")
    
    # 确保沪深300数据已初始化
    if BaseStrategy.hs300_df is None:
        BaseStrategy._initialize_hs300_data()
    
    if BaseStrategy.hs300_df is not None:
        # 测试用户提供的历史数据日期
        test_dates = [
            date(2025, 8, 1),
            date(2025, 8, 22),
            date(2025, 9, 5),
            date(2025, 9, 18),
            date(2025, 10, 15),
            date(2025, 11, 21)
        ]
        
        for test_date in test_dates:
            print(f"\n测试日期: {test_date}")
            
            # 模拟BaseStrategy.next方法中的市场状态判断逻辑
            market_state = '熊'  # 默认熊市
            
            try:
                # 获取当前日期
                current_date = test_date
                
                # 将current_date转换为datetime对象进行查找
                current_datetime = pd.Timestamp(current_date)
                print(f"转换为datetime: {current_datetime}")
                
                print(f"当前日期是否在索引中: {current_datetime in BaseStrategy.hs300_df.index}")
                
                if current_datetime in BaseStrategy.hs300_df.index:
                    row = BaseStrategy.hs300_df.loc[current_datetime]
                    print(f"找到数据: close={row['close']}, ma120={row['ma120']}")
                    if not pd.isna(row['ma120']):
                        # 当沪深300指数价格在120日移动平均线之上时为牛市，之下时为熊市
                        if row['close'] > row['ma120']:
                            market_state = '牛'
                            print("判断为牛市")
                        else:
                            market_state = '熊'
                            print("判断为熊市")
                    else:
                        # 移动平均线数据不足时保持默认状态
                        market_state = '熊'
                        print("ma120为空，保持默认熊市")
                else:
                    # 没有当前日期的数据时，尝试查找最接近的日期
                    print("当前日期不在索引中，查找最接近的日期")
                    # 将索引转换为date对象进行比较
                    index_dates = BaseStrategy.hs300_df.index.date
                    closest_idx = min(range(len(index_dates)), key=lambda i: abs(index_dates[i] - current_date))
                    closest_datetime = BaseStrategy.hs300_df.index[closest_idx]
                    print(f"最接近的日期: {closest_datetime.date()}")
                    row = BaseStrategy.hs300_df.loc[closest_datetime]
                    print(f"找到数据: close={row['close']}, ma120={row['ma120']}")
                    if not pd.isna(row['ma120']):
                        if row['close'] > row['ma120']:
                            market_state = '牛'
                            print("判断为牛市")
                        else:
                            market_state = '熊'
                            print("判断为熊市")
                    else:
                        market_state = '熊'
                        print("ma120为空，保持默认熊市")
            except Exception as e:
                print(f"计算市场状态失败: {e}")
                # 失败时保持默认状态
                market_state = '熊'
            
            print(f"最终市场状态: {market_state}")
    else:
        print("沪深300数据未初始化")


def debug_base_strategy_initialization():
    """调试BaseStrategy初始化逻辑"""
    print("\n=== 调试BaseStrategy初始化逻辑 ===")
    
    # 检查BaseStrategy类变量
    print(f"BaseStrategy.hs300_df是否为None: {BaseStrategy.hs300_df is None}")
    
    # 尝试直接初始化BaseStrategy.hs300_df
    if BaseStrategy.hs300_df is None:
        print("\n直接初始化BaseStrategy.hs300_df...")
        try:
            # 尝试从本地文件加载数据
            hs300_df = DataProvider.load_hs300_data()
            if hs300_df is not None and not hs300_df.empty:
                # 确保有120日移动平均线列
                if 'ma120' not in hs300_df.columns:
                    hs300_df['ma120'] = hs300_df['close'].rolling(window=120).mean()
                BaseStrategy.hs300_df = hs300_df
                print("成功初始化BaseStrategy.hs300_df")
            else:
                print("加载数据失败")
        except Exception as e:
            print(f"初始化失败: {e}")
    
    print(f"BaseStrategy.hs300_df是否为None: {BaseStrategy.hs300_df is None}")
    if BaseStrategy.hs300_df is not None:
        print(f"数据行数: {len(BaseStrategy.hs300_df)}")


if __name__ == "__main__":
    print("开始调试市场状态判断逻辑")
    
    # 调试沪深300指数数据初始化
    debug_hs300_data_initialization()
    
    # 调试市场状态判断逻辑
    debug_market_state_judgment()
    
    # 调试BaseStrategy初始化逻辑
    debug_base_strategy_initialization()
    
    print("\n调试完成")
