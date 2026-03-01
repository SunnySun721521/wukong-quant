#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试回测过程中的市场状态判断逻辑
"""

import os
import sys
from datetime import datetime, date
import pandas as pd

# 添加策略目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategy'))

from data_provider import DataProvider
from backtest_engine import BaseStrategy, BacktestEngine


def debug_base_strategy_initialization():
    """调试BaseStrategy初始化逻辑"""
    print("=== 调试BaseStrategy初始化逻辑 ===")
    
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
        print(f"索引类型: {type(BaseStrategy.hs300_df.index[0])}")
        print(f"索引范围: {BaseStrategy.hs300_df.index.min()} 到 {BaseStrategy.hs300_df.index.max()}")
        print(f"列名: {list(BaseStrategy.hs300_df.columns)}")


def debug_market_state_for_date(target_date):
    """调试指定日期的市场状态判断"""
    print(f"\n=== 调试日期 {target_date} 的市场状态判断 ===")
    
    # 确保BaseStrategy.hs300_df已初始化
    if BaseStrategy.hs300_df is None:
        debug_base_strategy_initialization()
    
    if BaseStrategy.hs300_df is not None:
        # 模拟BaseStrategy.next方法中的市场状态判断逻辑
        market_state = '熊'  # 默认熊市
        
        try:
            # 获取当前日期
            current_date = target_date
            
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
                index_dates = BaseStrategy.hs300_df.index
                closest_idx = min(range(len(index_dates)), key=lambda i: abs((index_dates[i] - current_datetime).days))
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
        return market_state
    else:
        print("沪深300数据未初始化")
        return '熊'


def debug_backtest_market_state():
    """调试回测过程中的市场状态判断"""
    print("\n=== 调试回测过程中的市场状态判断 ===")
    
    # 初始化BacktestEngine
    backtest_engine = BacktestEngine()
    
    # 测试单只股票的回测
    symbol = '002371'
    start_date = '20250801'
    end_date = '20251121'
    
    print(f"测试股票: {symbol}")
    print(f"测试日期范围: {start_date} 到 {end_date}")
    
    # 运行回测
    result = backtest_engine.run_backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        strategy_type='moving_average'
    )
    
    print(f"\n回测结果: {result}")
    if result:
        print(f"回测成功，交易次数: {len(result.get('trades', []))}")
        # 打印交易记录
        if 'trades' in result:
            print("\n交易记录:")
            for trade in result['trades']:
                print(f"日期: {trade['date']}, 类型: {trade['type']}, 价格: {trade['price']}, 数量: {trade['quantity']}, 市场状态: {trade.get('market_state', '未知')}")
    else:
        print("回测失败")


if __name__ == "__main__":
    print("开始调试回测过程中的市场状态判断逻辑")
    
    # 调试BaseStrategy初始化
    debug_base_strategy_initialization()
    
    # 调试指定日期的市场状态判断
    test_dates = [
        date(2025, 8, 1),
        date(2025, 8, 22),
        date(2025, 9, 5),
        date(2025, 9, 18),
        date(2025, 10, 15),
        date(2025, 11, 21)
    ]
    
    for test_date in test_dates:
        debug_market_state_for_date(test_date)
    
    # 调试回测过程中的市场状态判断
    debug_backtest_market_state()
    
    print("\n调试完成")
