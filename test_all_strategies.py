#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试所有策略是否正确应用了新的仓位计算逻辑
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategy.backtest_engine import BacktestEngine

def test_all_strategies():
    """测试所有策略"""
    print("=== 测试所有策略的仓位计算逻辑 ===")
    
    # 测试参数
    symbol = '002371'
    start_date = '20230101'
    end_date = '20260123'
    initial_cash = 1000000
    
    # 策略类型列表
    strategy_types = [
        'moving_average',
        'mean_reversion', 
        'momentum',
        'breakout',
        'niu_huicai'
    ]
    
    # 初始化回测引擎
    engine = BacktestEngine()
    
    for strategy_type in strategy_types:
        print(f"\n测试策略: {strategy_type}")
        
        # 运行单股票回测
        result = engine.run_backtest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            strategy_type=strategy_type,
            stock_initial_cash=initial_cash * 0.2  # 每只股票分配总资金的20%
        )
        
        if result:
            print(f"✓ 回测成功")
            print(f"  初始资金: {result['initial_cash']:.2f}")
            print(f"  最终资金: {result['final_value']:.2f}")
            print(f"  收益率: {result['total_return']:.2f}%")
            print(f"  交易次数: {result['total_trades']}")
            
            if result['trade_log']:
                print(f"  交易记录:")
                for trade in result['trade_log'][:3]:  # 只显示前3条
                    print(f"    {trade['date']} {trade['type']} {trade['price']:.2f} {trade['quantity']}")
        else:
            print(f"✗ 回测失败")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_all_strategies()
