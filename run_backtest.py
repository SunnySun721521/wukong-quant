#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
from strategy.backtest_engine import BacktestEngine

engine = BacktestEngine()
symbols = ['600519', '000858', '002371', '002415', '002236']

print("开始回测...")
results = []
for symbol in symbols:
    print(f"\n回测股票: {symbol}")
    result = engine.run_backtest(symbol, '20240101', '20250111', 5, 20)
    if result:
        results.append(result)
        print(f"  初始资金: {result['initial_cash']}")
        print(f"  最终价值: {result['final_value']}")
        print(f"  总收益率: {result['total_return']}%")
        print(f"  最大回撤: {result['max_drawdown']}%")
        print(f"  夏普比率: {result['sharpe_ratio']}")
        print(f"  总交易次数: {result['total_trades']}")
        print(f"  胜率: {result['win_rate']}%")
    else:
        print(f"  回测失败")

if results:
    print("\n" + "="*50)
    print("回测汇总：")
    print("="*50)
    for result in results:
        print(f"\n股票代码: {result['symbol']}")
        print(f"总收益率: {result['total_return']}%")
        print(f"最大回撤: {result['max_drawdown']}%")
        print(f"夏普比率: {result['sharpe_ratio']}")
        print(f"交易次数: {result['total_trades']}")
        print(f"胜率: {result['win_rate']}%")

print("\n回测完成！")