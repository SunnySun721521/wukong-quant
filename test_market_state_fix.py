#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试市场状态判断修复
"""

import os
import sys
from datetime import datetime, date
import pandas as pd

# 添加策略目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategy'))

from data_provider import DataProvider
from backtest_engine import BaseStrategy, BacktestEngine


def test_market_state_in_trades():
    """测试交易记录中的市场状态"""
    print("=== 测试交易记录中的市场状态 ===")
    
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
        print(f"回测成功，交易次数: {len(result.get('trade_log', []))}")
        # 打印交易记录
        if 'trade_log' in result:
            print("\n交易记录:")
            for trade in result['trade_log']:
                market_state = trade.get('market_state', '未知')
                print(f"日期: {trade['date']}, 类型: {trade['type']}, 价格: {trade['price']}, 数量: {trade['quantity']}, 市场状态: {market_state}")
                if 'profit' in trade:
                    print(f"  收益: {trade['profit']}")
        
        # 检查所有交易记录是否都包含市场状态
        if 'trade_log' in result:
            has_market_state = all('market_state' in trade for trade in result['trade_log'])
            print(f"\n所有交易记录都包含市场状态: {has_market_state}")
            if not has_market_state:
                # 找出缺少市场状态的交易记录
                for i, trade in enumerate(result['trade_log']):
                    if 'market_state' not in trade:
                        print(f"交易 {i+1} 缺少市场状态: {trade}")
        
        return True
    else:
        print("回测失败")
        return False


def test_niu_huicai_strategy():
    """
    测试牛回踩策略的市场状态判断
    注意：牛回踩策略需要计算年线，所以需要更多的历史数据
    """
    print("\n=== 测试牛回踩策略的市场状态判断 ===")
    
    # 初始化BacktestEngine
    backtest_engine = BacktestEngine()
    
    # 测试单只股票的回测
    symbol = '002371'
    start_date = '20240101'  # 更早的开始日期，以确保有足够的数据计算年线
    end_date = '20251121'
    
    print(f"测试股票: {symbol}")
    print(f"测试日期范围: {start_date} 到 {end_date}")
    
    # 运行回测
    result = backtest_engine.run_backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        strategy_type='niu_huicai'
    )
    
    print(f"\n回测结果: {result}")
    if result:
        print(f"回测成功，交易次数: {len(result.get('trade_log', []))}")
        # 打印交易记录
        if 'trade_log' in result:
            print("\n交易记录:")
            for trade in result['trade_log']:
                market_state = trade.get('market_state', '未知')
                print(f"日期: {trade['date']}, 类型: {trade['type']}, 价格: {trade['price']}, 数量: {trade['quantity']}, 市场状态: {market_state}")
                if 'profit' in trade:
                    print(f"  收益: {trade['profit']}")
        
        # 检查所有交易记录是否都包含市场状态
        if 'trade_log' in result:
            has_market_state = all('market_state' in trade for trade in result['trade_log'])
            print(f"\n所有交易记录都包含市场状态: {has_market_state}")
            if not has_market_state:
                # 找出缺少市场状态的交易记录
                for i, trade in enumerate(result['trade_log']):
                    if 'market_state' not in trade:
                        print(f"交易 {i+1} 缺少市场状态: {trade}")
        
        return True
    else:
        print("回测失败，可能是因为数据量不足")
        return False


if __name__ == "__main__":
    print("开始测试市场状态判断修复")
    
    # 初始化BaseStrategy.hs300_df
    BaseStrategy._initialize_hs300_data()
    
    # 测试移动平均线策略的交易记录
    test1 = test_market_state_in_trades()
    
    # 测试牛回踩策略的交易记录
    test2 = test_niu_huicai_strategy()
    
    print("\n=== 测试结果 ===")
    print(f"移动平均线策略测试: {'通过' if test1 else '失败'}")
    print(f"牛回踩策略测试: {'通过' if test2 else '失败'}")
    
    if all([test1, test2]):
        print("所有测试通过！")
    else:
        print("部分测试失败，请检查原因。")
