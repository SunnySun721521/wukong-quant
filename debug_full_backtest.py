#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试完整回测流程
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategy.backtest_engine import BacktestEngine

def debug_full_backtest():
    """调试完整回测流程"""
    print("=== 调试完整回测流程 ===")
    
    # 初始化回测引擎
    engine = BacktestEngine()
    
    # 测试参数
    symbol = '002371'
    start_date = '20230101'
    end_date = '20260123'
    strategy_type = 'niu_huicai'
    
    print(f"回测股票: {symbol}")
    print(f"时间范围: {start_date} 到 {end_date}")
    print(f"策略类型: {strategy_type}")
    
    # 运行单股票回测
    print("\n开始运行单股票回测...")
    result = engine.run_backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        strategy_type=strategy_type,
        position_pct=0.2,
        stock_initial_cash=500000
    )
    
    if result:
        print("\n=== 回测结果 ===")
        print(f"初始资金: {result['initial_cash']:.2f}")
        print(f"最终资金: {result['final_value']:.2f}")
        print(f"收益率: {result['total_return']:.2f}%")
        print(f"交易次数: {result['total_trades']}")
        print(f"交易记录: {len(result['trade_log'])} 条")
        
        if result['trade_log']:
            print("\n交易记录:")
            for trade in result['trade_log']:
                print(trade)
    else:
        print("\n回测失败，无结果")

if __name__ == "__main__":
    debug_full_backtest()
