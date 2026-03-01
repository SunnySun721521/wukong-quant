#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试市场状态由牛转熊时的减仓功能
"""

import os
import sys
from datetime import datetime, date
import pandas as pd

# 添加策略目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategy'))

from data_provider import DataProvider
from backtest_engine import BaseStrategy, BacktestEngine


def test_bull_to_bear_reduction():
    """测试牛转熊时的减仓功能"""
    print("=== 测试市场状态由牛转熊时的减仓功能 ===")
    
    # 初始化BacktestEngine
    backtest_engine = BacktestEngine()
    
    # 选择一个包含牛转熊的时间段
    # 2024-06-24: 牛 -> 熊
    symbol = '002371'
    start_date = '20240501'
    end_date = '20240731'
    
    print(f"测试股票: {symbol}")
    print(f"测试日期范围: {start_date} 到 {end_date}")
    print(f"预期在 2024-06-24 附近发生牛转熊转换")
    
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
        
        # 检查是否有"市场由牛转熊"的卖出记录
        if 'trade_log' in result:
            print("\n详细交易日志:")
            for log in result['trade_log']:
                reason = log.get('reason', '无')
                print(f"日期: {log['date']}, 类型: {log['type']}, 价格: {log['price']}, 数量: {log['quantity']}, 市场状态: {log.get('market_state', '未知')}, 原因: {reason}")
                
                if reason == '市场由牛转熊':
                    print(f"  ✓ 找到牛转熊减仓记录！卖出数量: {log['quantity']}股")
    else:
        print("回测失败")


if __name__ == "__main__":
    print("开始测试市场状态由牛转熊时的减仓功能")
    
    test_bull_to_bear_reduction()
    
    print("\n测试完成")
