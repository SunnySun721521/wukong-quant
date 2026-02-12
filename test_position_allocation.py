#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategy.backtest_engine import BacktestEngine

# 测试每股初始资金按照仓位管理策略分配
def test_position_allocation():
    print("测试每股初始资金按照仓位管理策略分配...")
    
    # 初始化回测引擎
    backtest_engine = BacktestEngine(initial_cash=1000000)
    
    # 测试多股票回测，使用3只股票
    symbols = ["000001", "600519", "000858"]
    start_date = "20230101"
    end_date = "20230331"
    initial_cash = 1000000
    
    print(f"总初始资金: {initial_cash}")
    print(f"股票数量: {len(symbols)}")
    expected_per_stock_cash = initial_cash / len(symbols)
    print(f"预期每只股票初始资金: {expected_per_stock_cash}")
    
    # 运行多股票回测
    result = backtest_engine.run_multi_stock_backtest(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_cash=initial_cash
    )
    
    if result:
        print("\n回测结果:")
        print(f"总初始资金: {result['initial_cash']}")
        print(f"总最终价值: {result['final_value']}")
        print(f"总收益率: {result['total_return']}%")
        print(f"总交易次数: {result['total_trades']}")
        
        print("\n个股回测结果:")
        for stock_result in result['individual_results']:
            print(f"\n股票: {stock_result['symbol']}")
            print(f"初始资金: {stock_result['initial_cash']}")
            print(f"最终价值: {stock_result['final_value']}")
            print(f"收益率: {stock_result['total_return']}%")
            print(f"交易次数: {stock_result['total_trades']}")
            
            # 验证初始资金是否正确分配
            if abs(stock_result['initial_cash'] - expected_per_stock_cash) < 0.01:
                print(f"✅ 初始资金分配正确: {stock_result['initial_cash']} = {expected_per_stock_cash}")
            else:
                print(f"❌ 初始资金分配错误: {stock_result['initial_cash']} != {expected_per_stock_cash}")
    else:
        print("回测失败")

if __name__ == "__main__":
    test_position_allocation()
