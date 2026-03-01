#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategy.data_provider import DataProvider
from strategy.backtest_engine import BacktestEngine

# 测试DataProvider
print("测试DataProvider...")
symbol = "000001"
start_date = "20230101"
end_date = "20231231"

df = DataProvider.get_kline_data(symbol, start_date, end_date)
print(f"获取到的K线数据: {df.shape if df is not None else 'None'}")
if df is not None:
    print(f"数据头5行:\n{df.head()}")
    print(f"数据尾5行:\n{df.tail()}")
else:
    print("未获取到数据")

# 测试BacktestEngine
print("\n测试BacktestEngine...")
backtest_engine = BacktestEngine(initial_cash=1000000)
result = backtest_engine.run_backtest(symbol, start_date, end_date, fast_period=5, slow_period=20)
print(f"回测结果: {'成功' if result else '失败'}")
if result:
    print(f"初始资金: {result['initial_cash']}")
    print(f"最终价值: {result['final_value']}")
    print(f"总收益率: {result['total_return']}%")
    print(f"总交易次数: {result['total_trades']}")
    print(f"收益曲线点数: {len(result['equity_curve'])}")
    print(f"交易记录数: {len(result['trade_log'])}")
    
    # 打印前几个交易记录
    if result['trade_log']:
        print(f"\n前5条交易记录:\n{result['trade_log'][:5]}")
    
    # 测试多股票回测
    print("\n测试多股票回测...")
    multi_result = backtest_engine.run_multi_stock_backtest(["000001"], start_date, end_date, fast_period=5, slow_period=20)
    if multi_result:
        print(f"多股票回测成功，总收益率: {multi_result['total_return']}%")
        print(f"多股票回测最终价值: {multi_result['final_value']}")
        print(f"多股票回测总交易次数: {multi_result['total_trades']}")
        print(f"多股票回测收益曲线点数: {len(multi_result['equity_curve'])}")
        print(f"多股票回测交易记录数: {sum(len(r['trade_log']) for r in multi_result['individual_results'])}")
    else:
        print("多股票回测失败")
