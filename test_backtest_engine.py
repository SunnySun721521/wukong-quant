#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'strategy'))

from strategy.backtest_engine import BacktestEngine

engine = BacktestEngine()
result = engine.run_backtest('600519', '20240101', '20250111', 5, 20)

if result:
    print("回测成功！")
    print(f"初始资金: {result['initial_cash']}")
    print(f"最终价值: {result['final_value']}")
    print(f"总收益率: {result['total_return']}%")
    print(f"最大回撤: {result['max_drawdown']}%")
    print(f"夏普比率: {result['sharpe_ratio']}")
    print(f"总交易次数: {result['total_trades']}")
    print(f"胜率: {result['win_rate']}%")
else:
    print("回测失败！")