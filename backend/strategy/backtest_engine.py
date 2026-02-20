#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测引擎模块 - 提供股票回测功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .data_provider import DataProvider

class BacktestEngine:
    """回测引擎类"""
    
    def __init__(self, initial_cash=100000):
        self.results = {}
        self.initial_cash = initial_cash
    
    def _get_hs300_data(self, start_date, end_date):
        """获取沪深300指数数据"""
        try:
            import baostock as bs
            lg = bs.login()
            if lg.error_code != '0':
                print(f"baostock登录失败: {lg.error_msg}")
                return None
            
            # 获取沪深300指数数据
            rs = bs.query_history_k_data_plus(
                "sh.000300",
                "date,open,high,low,close,volume",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3"
            )
            
            if rs.error_code != '0':
                print(f"获取沪深300数据失败: {rs.error_msg}")
                bs.logout()
                return None
            
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            bs.logout()
            
            if not data_list:
                return None
            
            df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print(f"获取沪深300数据成功: {len(df)}条记录")
            return df
            
        except Exception as e:
            print(f"获取沪深300数据异常: {e}")
            return None
    
    def _is_bull_market_by_hs300(self, hs300_df, target_date):
        """根据沪深300指数判断牛熊市（使用MA250年线）"""
        try:
            if hs300_df is None or len(hs300_df) < 250:
                print("沪深300数据不足250天，默认牛市")
                return True
            
            hs300_df = hs300_df.sort_index()
            target_date_pd = pd.to_datetime(target_date)
            
            mask = hs300_df.index <= target_date_pd
            df_before = hs300_df[mask]
            
            if len(df_before) < 250:
                print(f"目标日期前数据不足250天，默认牛市")
                return True
            
            recent_250 = df_before.tail(250)
            ma250 = recent_250['close'].mean()
            current_price = recent_250['close'].iloc[-1]
            
            is_bull = current_price > ma250
            print(f"沪深300牛熊市判断: 日期={target_date}, 价格={current_price:.2f}, MA250={ma250:.2f}, 结果={'牛市' if is_bull else '熊市'}")
            return is_bull
            
        except Exception as e:
            print(f"沪深300牛熊市判断异常: {e}")
            return True

    def _get_market_state_for_date(self, hs300_df, target_date):
        """获取指定日期的市场状态（返回'牛'或'熊'）"""
        is_bull = self._is_bull_market_by_hs300(hs300_df, target_date)
        return '牛' if is_bull else '熊'
    
    def run_multi_stock_backtest(self, symbols, start_date, end_date, 
                                 fast_period=5, slow_period=20,
                                 initial_cash=1000000, transaction_cost=0.0003,
                                 strategy_type='moving_average'):
        """
        运行多股票回测
        
        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            fast_period: 快速均线周期
            slow_period: 慢速均线周期
            initial_cash: 初始资金
            transaction_cost: 交易成本
            strategy_type: 策略类型
        
        Returns:
            dict: 回测结果
        """
        try:
            individual_results = []
            all_trades = []
            equity_curves = {}

            print(f"多股回测开始: symbols={symbols}, initial_cash={initial_cash}, len(symbols)={len(symbols)}")

            # 资金分配逻辑：
            # 基础资金 = 总资金 * 80% * 20% = 总资金 * 16%，最大16万（这是每只股票的初始资金）
            # 牛市：全部基础资金买入
            # 熊市：只买入基础资金 * 30%
            base_cash_per_stock = min(initial_cash * 0.8 * 0.2, 160000)
            print(f"资金分配: 基础资金={base_cash_per_stock}")

            # 获取沪深300指数数据（用于动态判断牛熊市）
            # 处理日期格式：支持 YYYYMMDD 和 YYYY-MM-DD 两种格式
            if '-' in start_date:
                start_date_fmt = start_date
            else:
                start_date_fmt = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
            
            if '-' in end_date:
                end_date_fmt = end_date
            else:
                end_date_fmt = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
            
            hs300_start = (datetime.strptime(start_date_fmt, '%Y-%m-%d') - timedelta(days=400)).strftime('%Y-%m-%d')
            hs300_df = self._get_hs300_data(hs300_start, end_date_fmt)
            
            print(f"沪深300数据获取完成: {len(hs300_df) if hs300_df is not None else 0}条记录")

            for symbol in symbols:
                df = DataProvider.get_kline_data(symbol, start_date, end_date)
                if df is not None and not df.empty and len(df) >= slow_period + 10:
                    print(f"单股回测: symbol={symbol}, 基础资金={base_cash_per_stock}")
                    result = self._backtest_single_stock(
                        symbol, df, fast_period, slow_period,
                        base_cash_per_stock, transaction_cost, strategy_type,
                        hs300_df
                    )
                    if result:
                        individual_results.append(result)
                        all_trades.extend(result.get('trades', []))
                        equity_curves[symbol] = result.get('equity_curve', [])

            if not individual_results:
                return None

            # 计算实际使用的初始资金
            actual_initial_cash = sum(r['initial_cash'] for r in individual_results)

            # 计算组合收益
            total_return = sum(r['return'] for r in individual_results) / len(individual_results)

            # 计算组合权益曲线
            combined_equity_curve = self._combine_equity_curves(equity_curves, actual_initial_cash)

            # 计算真实回测指标
            max_drawdown = self._calculate_max_drawdown(combined_equity_curve)
            sharpe_ratio = self._calculate_sharpe_ratio(combined_equity_curve)
            win_rate = self._calculate_win_rate(all_trades)
            profit_factor = self._calculate_profit_factor(all_trades)
            
            # 计算最终价值
            final_value = combined_equity_curve[-1]['value'] if combined_equity_curve else actual_initial_cash

            return {
                'initial_cash': actual_initial_cash,
                'final_value': round(final_value, 2),
                'total_return': round(total_return, 4),
                'max_drawdown': round(max_drawdown, 4),
                'sharpe_ratio': round(sharpe_ratio, 4),
                'total_trades': len(all_trades),
                'win_rate': round(win_rate, 4),
                'profit_factor': round(profit_factor, 4),
                'individual_results': individual_results,
                'equity_curve': combined_equity_curve
            }

        except Exception as e:
            print(f"回测失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _backtest_single_stock(self, symbol, df, fast_period, slow_period,
                               base_cash, transaction_cost, strategy_type,
                               hs300_df):
        """单股票回测 - 包含止盈止损和动态市场状态判断
        
        Args:
            base_cash: 基础资金（用于显示初始资金）
            hs300_df: 沪深300指数数据（用于动态判断牛熊市）
        """
        try:
            print(f"单股回测开始: symbol={symbol}, base_cash={base_cash}, strategy_type={strategy_type}")

            df = df.copy()

            # 根据不同策略生成交易信号
            if strategy_type == 'niu_huicai' or strategy_type == 'bull_retracement':
                df = self._generate_bull_retracement_signals(df)
            elif strategy_type == 'mean_reversion':
                df = self._generate_mean_reversion_signals(df)
            elif strategy_type == 'momentum':
                df = self._generate_momentum_signals(df)
            elif strategy_type == 'breakout':
                df = self._generate_breakout_signals(df)
            else:
                df = self._generate_moving_average_signals(df, fast_period, slow_period)

            print(f"交易信号统计: 买入信号={(df['position'] == 1).sum()}, 卖出信号={(df['position'] == -1).sum()}")

            # 模拟交易 - 动态市场状态判断
            bull_cash = base_cash  # 牛市：全部基础资金
            bear_cash = base_cash * 0.3  # 熊市：30%基础资金
            
            cash = base_cash  # 初始资金
            position = 0
            buy_price = 0
            trades = []
            equity_curve = []
            current_market_state = None
            last_market_state = None

            TAKE_PROFIT_RATE = 0.10
            STOP_LOSS_RATE = 0.04

            print(f"开始模拟交易: base_cash={base_cash}, 牛市资金={bull_cash}, 熊市资金={bear_cash}")

            for i in range(len(df)):
                price = df['close'].iloc[i]
                date = df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i])

                # 动态判断当前市场状态
                current_market_state = self._get_market_state_for_date(hs300_df, date)
                
                # 检测牛熊转换
                if last_market_state is not None and last_market_state != current_market_state:
                    print(f"市场状态转换: {last_market_state} -> {current_market_state}, date={date}")
                    if last_market_state == '牛' and current_market_state == '熊' and position > 0:
                        bear_value = bear_cash
                        current_value = position * price
                        if current_value > bear_value:
                            sell_shares = int((current_value - bear_value) / price)
                            if sell_shares > 0 and sell_shares <= position:
                                revenue = sell_shares * price * (1 - transaction_cost)
                                profit = revenue - (sell_shares * buy_price)
                                cash += revenue
                                position -= sell_shares
                                trades.append({
                                    'date': date, 'type': 'sell', 'price': price,
                                    'shares': sell_shares, 'revenue': revenue,
                                    'profit': profit, 'reason': '牛转熊减仓',
                                    'market_state': '熊'
                                })
                                print(f"牛转熊减仓: date={date}, shares={sell_shares}")
                last_market_state = current_market_state

                # 止盈止损检查
                if position > 0 and buy_price > 0:
                    profit_rate = (price - buy_price) / buy_price
                    
                    if profit_rate >= TAKE_PROFIT_RATE:
                        revenue = position * price * (1 - transaction_cost)
                        profit = revenue - (position * buy_price)
                        cash += revenue
                        trades.append({
                            'date': date, 'type': 'sell', 'price': price,
                            'shares': position, 'revenue': revenue,
                            'profit': profit, 'reason': '止盈',
                            'market_state': current_market_state
                        })
                        print(f"止盈卖出: date={date}, shares={position}, profit={profit}")
                        position = 0
                        buy_price = 0
                        continue
                    
                    if profit_rate <= -STOP_LOSS_RATE:
                        revenue = position * price * (1 - transaction_cost)
                        profit = revenue - (position * buy_price)
                        cash += revenue
                        trades.append({
                            'date': date, 'type': 'sell', 'price': price,
                            'shares': position, 'revenue': revenue,
                            'profit': profit, 'reason': '止损',
                            'market_state': current_market_state
                        })
                        print(f"止损卖出: date={date}, shares={position}, profit={profit}")
                        position = 0
                        buy_price = 0
                        continue

                # 策略买入信号
                if df['position'].iloc[i] == 1 and position == 0:
                    buy_cash = bull_cash if current_market_state == '牛' else bear_cash
                    actual_buy = min(cash, buy_cash)
                    if actual_buy > 0:
                        shares = int(actual_buy / (price * (1 + transaction_cost)))
                        if shares > 0:
                            cost = shares * price * (1 + transaction_cost)
                            cash -= cost
                            position += shares
                            buy_price = price
                            trades.append({
                                'date': date, 'type': 'buy', 'price': price,
                                'shares': shares, 'cost': cost,
                                'market_state': current_market_state
                            })
                            print(f"买入: date={date}, shares={shares}, cost={cost}, 市场状态={current_market_state}")

                # 策略卖出信号
                elif df['position'].iloc[i] == -1 and position > 0:
                    revenue = position * price * (1 - transaction_cost)
                    profit = revenue - (position * buy_price)
                    cash += revenue
                    trades.append({
                        'date': date, 'type': 'sell', 'price': price,
                        'shares': position, 'revenue': revenue,
                        'profit': profit, 'reason': '策略信号',
                        'market_state': current_market_state
                    })
                    print(f"策略卖出: date={date}, shares={position}, profit={profit}")
                    position = 0
                    buy_price = 0

                equity = cash + position * price
                equity_curve.append({'date': date, 'value': round(equity, 2)})

            print(f"交易完成: trades={len(trades)}, final_cash={cash}, final_position={position}, final_equity={cash + position * df['close'].iloc[-1]}")

            # 计算最终收益
            final_price = df['close'].iloc[-1]
            final_equity = cash + position * final_price
            total_return = (final_equity - base_cash) / base_cash

            # 获取股票名称
            stock_info = DataProvider.get_stock_info(symbol)
            name = stock_info['name'] if stock_info else symbol

            print(f"单股回测完成: symbol={symbol}, name={name}, final_equity={final_equity}, total_return={total_return}, trades={len(trades)}, equity_curve={len(equity_curve)}")

            return {
                'symbol': symbol,
                'name': name,
                'return': round(total_return, 4),
                'trades': trades,
                'equity_curve': equity_curve,
                'final_equity': round(final_equity, 2),
                'initial_cash': base_cash,
                'market_state': '动态判断'
            }

        except Exception as e:
            print(f"单股回测失败 {symbol}: {e}")
            return None

    def _combine_equity_curves(self, equity_curves, initial_cash):
        """合并多个股票的权益曲线"""
        if not equity_curves:
            return []

        all_dates = set()
        for curve in equity_curves.values():
            all_dates.update([p['date'] for p in curve])
        all_dates = sorted(list(all_dates))

        per_stock_initial = initial_cash / len(equity_curves) if equity_curves else initial_cash

        combined = []
        for date in all_dates:
            total_value = 0
            for symbol, curve in equity_curves.items():
                value = 0
                found = False
                last_value = per_stock_initial
                
                for p in curve:
                    if p['date'] == date:
                        value = p['value']
                        found = True
                        break
                    elif p['date'] < date:
                        last_value = p['value']
                
                if not found:
                    value = last_value
                
                total_value += value
            combined.append({'date': date, 'value': total_value})

        return combined

    def _calculate_max_drawdown(self, equity_curve):
        """计算最大回撤"""
        if not equity_curve:
            return 0

        values = [p['value'] for p in equity_curve]
        peak = values[0]
        max_drawdown = 0

        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)

        return max_drawdown

    def _calculate_sharpe_ratio(self, equity_curve, risk_free_rate=0.03):
        """计算夏普比率"""
        if not equity_curve or len(equity_curve) < 2:
            return 0

        values = [p['value'] for p in equity_curve]
        returns = []

        for i in range(1, len(values)):
            daily_return = (values[i] - values[i-1]) / values[i-1]
            returns.append(daily_return)

        if not returns:
            return 0

        avg_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0

        # 年化夏普比率
        sharpe = (avg_return * 252 - risk_free_rate) / (std_return * np.sqrt(252))
        return sharpe

    def _calculate_win_rate(self, trades):
        """计算胜率"""
        if not trades:
            return 0

        sell_trades = [t for t in trades if t['type'] == 'sell']
        if not sell_trades:
            return 0

        win_count = sum(1 for t in sell_trades if t.get('profit', 0) > 0)
        return win_count / len(sell_trades)

    def _calculate_profit_factor(self, trades):
        """计算盈亏比"""
        if not trades:
            return 0

        sell_trades = [t for t in trades if t['type'] == 'sell']
        if not sell_trades:
            return 0

        total_profit = sum(t['profit'] for t in sell_trades if t.get('profit', 0) > 0)
        total_loss = abs(sum(t['profit'] for t in sell_trades if t.get('profit', 0) < 0))

        if total_loss == 0:
            return total_profit if total_profit > 0 else 0

        return total_profit / total_loss

    def _generate_moving_average_signals(self, df, fast_period, slow_period):
        """移动平均线策略"""
        df['ma_fast'] = df['close'].rolling(window=fast_period).mean()
        df['ma_slow'] = df['close'].rolling(window=slow_period).mean()

        print(f"移动平均线策略: df长度={len(df)}, fast_period={fast_period}, slow_period={slow_period}")

        df['signal'] = 0
        for i in range(fast_period, len(df)):
            if df['ma_fast'].iloc[i] > df['ma_slow'].iloc[i]:
                df['signal'].iloc[i] = 1
            else:
                df['signal'].iloc[i] = 0

        df['position'] = df['signal'].diff()
        df['position'] = df['position'].fillna(0)
        print(f"移动平均线策略: 买入信号={(df['position'] == 1).sum()}, 卖出信号={(df['position'] == -1).sum()}")
        return df

    def _generate_bull_retracement_signals(self, df):
        """牛回踩策略"""
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma250'] = df['close'].rolling(window=250).mean()
        df['v_ma5'] = df['volume'].rolling(window=5).mean()
        df['v_ma60'] = df['volume'].rolling(window=60).mean()

        print(f"牛回踩策略: df长度={len(df)}, 需要至少250天数据")

        df['signal'] = 0
        for i in range(250, len(df)):
            # 买入条件：股价 > 年线 AND 5日均量 > 60日均量 AND 缩量 AND 回踩20日线
            if (df['close'].iloc[i] > df['ma250'].iloc[i] and
                df['v_ma5'].iloc[i] > df['v_ma60'].iloc[i] and
                df['volume'].iloc[i] < df['v_ma5'].iloc[i] * 0.8 and
                abs(df['close'].iloc[i] / df['ma20'].iloc[i] - 1) < 0.015):
                df['signal'].iloc[i] = 1
            # 卖出：只通过止盈止损和牛转熊机制，不使用策略卖出信号
            else:
                df['signal'].iloc[i] = df['signal'].iloc[i-1] if i > 0 else 0

        df['position'] = df['signal'].diff()
        df['position'] = df['position'].fillna(0)
        print(f"牛回踩策略: 买入信号={(df['position'] == 1).sum()}, 卖出信号={(df['position'] == -1).sum()}")
        return df

    def _generate_mean_reversion_signals(self, df):
        """均值回归策略"""
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['std20'] = df['close'].rolling(window=20).std()
        df['upper_band'] = df['ma20'] + 2 * df['std20']
        df['lower_band'] = df['ma20'] - 2 * df['std20']

        df['signal'] = 0
        for i in range(20, len(df)):
            if df['close'].iloc[i] < df['lower_band'].iloc[i]:
                df['signal'].iloc[i] = 1
            elif df['close'].iloc[i] > df['upper_band'].iloc[i]:
                df['signal'].iloc[i] = 0
            else:
                df['signal'].iloc[i] = df['signal'].iloc[i-1]

        df['position'] = df['signal'].diff()
        df['position'] = df['position'].fillna(0)
        return df

    def _generate_momentum_signals(self, df):
        """动量策略"""
        df['momentum'] = df['close'].pct_change(periods=10)
        df['ma_momentum'] = df['momentum'].rolling(window=5).mean()

        df['signal'] = 0
        for i in range(15, len(df)):
            # 买入条件：动量 > 0 且动量均值 > 0
            if df['momentum'].iloc[i] > 0 and df['ma_momentum'].iloc[i] > 0:
                df['signal'].iloc[i] = 1
            # 卖出条件：动量 < 0 或动量均值 < 0
            elif df['momentum'].iloc[i] < 0 or df['ma_momentum'].iloc[i] < 0:
                df['signal'].iloc[i] = 0
            # 保持之前的状态
            else:
                df['signal'].iloc[i] = df['signal'].iloc[i-1] if i > 0 else 0

        df['position'] = df['signal'].diff()
        df['position'] = df['position'].fillna(0)
        return df

    def _generate_breakout_signals(self, df):
        """突破策略"""
        df['high_20'] = df['high'].rolling(window=20).max()
        df['low_20'] = df['low'].rolling(window=20).min()

        df['signal'] = 0
        for i in range(20, len(df)):
            if df['close'].iloc[i] > df['high_20'].iloc[i-1]:
                df['signal'].iloc[i] = 1
            elif df['close'].iloc[i] < df['low_20'].iloc[i-1]:
                df['signal'].iloc[i] = 0
            else:
                df['signal'].iloc[i] = df['signal'].iloc[i-1]

        df['position'] = df['signal'].diff()
        df['position'] = df['position'].fillna(0)
        return df
