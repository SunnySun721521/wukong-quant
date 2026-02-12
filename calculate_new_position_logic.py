#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
按照新的资金分配逻辑重新计算回测
新逻辑：
1. 每只股票分配的资金 = 总最终资金 × 20%
2. 购买资金 = 每只股票分配的资金 × 市场仓位比例（牛市80%，熊市30%）
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategy.backtest_engine import BacktestEngine

def calculate_new_position_logic():
    """按照新的资金分配逻辑计算"""
    print("=== 按照新资金分配逻辑计算 ===")
    
    # 测试参数
    symbols = ['002371', '300274']
    start_date = '20230101'
    end_date = '20260123'
    strategy_type = 'niu_huicai'
    initial_total_cash = 1000000
    
    print(f"回测股票: {symbols}")
    print(f"时间范围: {start_date} 到 {end_date}")
    print(f"策略类型: {strategy_type}")
    print(f"初始总资金: {initial_total_cash:.2f} 元")
    
    # 初始化回测引擎
    engine = BacktestEngine()
    
    # 首先运行原逻辑的回测，获取总最终资金
    print("\n1. 运行原逻辑回测获取总最终资金...")
    original_result = engine.run_multi_stock_backtest(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        strategy_type=strategy_type,
        initial_cash=initial_total_cash
    )
    
    if not original_result:
        print("回测失败，无法获取总最终资金")
        return
    
    total_final_cash = original_result['final_value']
    print(f"总最终资金: {total_final_cash:.2f} 元")
    
    # 计算每只股票分配的资金（总最终资金的20%）
    per_stock_allocated_cash = total_final_cash * 0.2
    print(f"每只股票分配的资金: {per_stock_allocated_cash:.2f} 元")
    
    # 市场仓位比例
    market_position_ratios = {
        '牛': 0.8,  # 牛市80%
        '熊': 0.3   # 熊市30%
    }
    
    print("\n2. 按照新逻辑重新计算每只股票的交易...")
    
    # 对每只股票重新计算
    new_results = []
    for symbol in symbols:
        print(f"\n处理股票: {symbol}")
        
        # 运行单股票回测获取原始交易记录
        stock_result = engine.run_backtest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            strategy_type=strategy_type,
            stock_initial_cash=per_stock_allocated_cash
        )
        
        if not stock_result:
            print(f"股票 {symbol} 回测失败")
            continue
        
        # 重新计算每笔交易的购买资金和数量
        new_trade_log = []
        for trade in stock_result['trade_log']:
            if trade['type'] == 'buy':
                # 获取市场状态
                market_state = trade.get('market_state', '熊')
                position_ratio = market_position_ratios.get(market_state, 0.3)
                
                # 新的购买资金 = 每只股票分配的资金 × 市场仓位比例
                new_buy_cash = per_stock_allocated_cash * position_ratio
                
                # 新的购买数量 = 新的购买资金 / 购买价格
                new_quantity = int(new_buy_cash / trade['price'])
                
                # 更新交易记录
                new_trade = trade.copy()
                new_trade['allocated_cash'] = per_stock_allocated_cash
                new_trade['position_ratio'] = position_ratio
                new_trade['buy_cash'] = new_buy_cash
                new_trade['quantity'] = new_quantity
                new_trade_log.append(new_trade)
            else:
                # 卖出交易，保持数量与对应买入一致
                if new_trade_log and new_trade_log[-1]['type'] == 'buy':
                    new_trade = trade.copy()
                    new_trade['quantity'] = new_trade_log[-1]['quantity']
                    # 重新计算盈亏
                    buy_trade = new_trade_log[-1]
                    new_trade['profit'] = (new_trade['price'] - buy_trade['price']) * new_trade['quantity']
                    new_trade_log.append(new_trade)
                else:
                    new_trade_log.append(trade.copy())
        
        # 计算新的总盈亏
        total_profit = 0
        for trade in new_trade_log:
            if trade['type'] == 'sell' and 'profit' in trade:
                total_profit += trade['profit']
        
        # 计算新的最终资金
        new_final_cash = per_stock_allocated_cash + total_profit
        
        print(f"股票 {symbol}:")
        print(f"  分配资金: {per_stock_allocated_cash:.2f} 元")
        print(f"  新最终资金: {new_final_cash:.2f} 元")
        print(f"  总盈亏: {total_profit:.2f} 元")
        print(f"  交易次数: {len(new_trade_log)}")
        
        # 打印详细交易记录
        if new_trade_log:
            print("  交易记录:")
            print("    日期\t\t类型\t价格\t数量\t盈亏\t市场状态\t仓位比例")
            for trade in new_trade_log:
                date = trade['date']
                trade_type = trade['type']
                price = trade['price']
                quantity = trade['quantity']
                profit = trade.get('profit', 0)
                market_state = trade.get('market_state', '未知')
                position_ratio = trade.get('position_ratio', 0)
                
                print(f"    {date}\t{trade_type}\t{price:.2f}\t{quantity}\t{profit:.2f}\t{market_state}\t{position_ratio:.2f}")
        
        new_results.append({
            'symbol': symbol,
            'allocated_cash': per_stock_allocated_cash,
            'final_cash': new_final_cash,
            'profit': total_profit,
            'trade_log': new_trade_log
        })
    
    # 计算总体结果
    if new_results:
        total_allocated = sum(r['allocated_cash'] for r in new_results)
        total_final = sum(r['final_cash'] for r in new_results)
        total_profit = sum(r['profit'] for r in new_results)
        
        print("\n=== 总体结果 ===")
        print(f"总分配资金: {total_allocated:.2f} 元")
        print(f"总最终资金: {total_final:.2f} 元")
        print(f"总盈亏: {total_profit:.2f} 元")
        print(f"总收益率: {(total_profit / total_allocated * 100):.2f}%")
    
    print("\n=== 计算完成 ===")

if __name__ == "__main__":
    calculate_new_position_logic()
