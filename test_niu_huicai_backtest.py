#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试牛回踩策略回测
股票：002371 和 300274
时间范围：2023-01-01 到 2026-01-23
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategy.backtest_engine import BacktestEngine

def test_niu_huicai_backtest():
    """测试牛回踩策略回测"""
    print("=== 开始牛回踩策略回测 ===")
    
    # 初始化回测引擎
    engine = BacktestEngine(initial_cash=1000000)
    
    # 测试参数
    symbols = ['002371', '300274']
    start_date = '2023-01-01'
    end_date = '2026-01-23'
    strategy_type = 'niu_huicai'  # 牛回踩策略
    
    print(f"回测股票: {symbols}")
    print(f"时间范围: {start_date} 到 {end_date}")
    print(f"策略类型: {strategy_type}")
    
    # 运行多股票回测
    print("\n开始运行多股票回测...")
    result = engine.run_multi_stock_backtest(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        strategy_type=strategy_type,
        initial_cash=1000000
    )
    
    if result:
        print("\n=== 回测结果摘要 ===")
        print(f"总初始资金: {result['initial_cash']:.2f}")
        print(f"总最终资金: {result['final_value']:.2f}")
        print(f"总收益率: {result['total_return']:.2f}%")
        print(f"最大回撤: {result['max_drawdown']:.2f}%")
        print(f"总交易次数: {result['total_trades']}")
        print(f"胜率: {result['win_rate']:.2f}%")
        
        # 打印每只股票的详细交易记录
        print("\n=== 详细交易记录 ===")
        for i, stock_result in enumerate(result['individual_results']):
            symbol = stock_result['symbol']
            trade_log = stock_result['trade_log']
            
            print(f"\n股票: {symbol}")
            print(f"交易次数: {len(trade_log)}")
            
            if trade_log:
                print("交易记录:")
                print("日期\t\t类型\t价格\t数量\t盈亏\t市场状态")
                print("-" * 80)
                
                for trade in trade_log:
                    date = trade['date']
                    trade_type = trade['type']
                    price = trade['price']
                    quantity = trade['quantity']
                    profit = trade.get('profit', 0)
                    market_state = trade.get('market_state', '未知')
                    
                    # 格式化输出
                    print(f"{date}\t{trade_type}\t{price:.2f}\t{quantity}\t{profit:.2f}\t{market_state}")
            else:
                print("无交易记录")
    else:
        print("回测失败，无结果")
    
    print("\n=== 回测完成 ===")

if __name__ == "__main__":
    test_niu_huicai_backtest()
