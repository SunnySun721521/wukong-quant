#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_provider import DataProvider

class BaseStrategy(bt.Strategy):
    """基础策略类，包含市场状态判断和仓位控制逻辑"""
    params = (
        ('position_pct', 0.2),
        ('initial_cash', 1000000),  # 初始资金
    )
    
    # 类变量，存储沪深300指数数据，所有策略实例共享
    hs300_df = None
    
    def __init__(self):
        self.trade_log = []
        self.equity_curve = []
        self.buy_price = 0  # 记录买入价格
        self.buy_quantity = 0  # 记录买入数量
        self.market_state = '熊'  # 默认熊市
        self.previous_market_state = '熊'  # 之前的市场状态
        
        # 初始化沪深300指数数据（仅在第一次初始化时）
        if BaseStrategy.hs300_df is None:
            BaseStrategy._initialize_hs300_data()
    
    @classmethod
    def _initialize_hs300_data(cls):
        """初始化沪深300指数数据"""
        try:
            import os
            from data_provider import DataProvider
            
            # 检查数据文件是否需要更新
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            data_file = os.path.join(data_dir, 'hs300_data.csv')
            need_update = False
            
            if os.path.exists(data_file):
                # 检查文件最后修改时间
                file_mtime = os.path.getmtime(data_file)
                current_time = datetime.now().timestamp()
                # 如果文件超过24小时未更新，需要更新
                if current_time - file_mtime > 24 * 60 * 60:
                    need_update = True
                    print("沪深300指数数据文件超过24小时未更新，需要更新")
            else:
                # 文件不存在，需要下载
                need_update = True
            
            # 如果需要更新，调用更新方法
            if need_update:
                print("开始更新沪深300指数数据")
                update_success = DataProvider.update_hs300_data()
                if not update_success:
                    print("更新沪深300指数数据失败，尝试从本地文件加载")
            
            # 尝试从本地文件加载数据
            hs300_df = DataProvider.load_hs300_data()
            
            if hs300_df is not None and not hs300_df.empty:
                # 确保有120日移动平均线列
                if 'ma120' not in hs300_df.columns:
                    hs300_df['ma120'] = hs300_df['close'].rolling(window=120).mean()
                cls.hs300_df = hs300_df
                print("从本地文件成功初始化沪深300指数数据")
            else:
                # 如果本地文件不存在或为空，尝试下载数据
                print("本地沪深300指数数据不存在，开始下载")
                hs300_df = DataProvider.download_hs300_data()
                if hs300_df is not None and not hs300_df.empty:
                    # 保存到本地文件
                    DataProvider.save_hs300_data(hs300_df)
                    cls.hs300_df = hs300_df
                    print("下载并初始化沪深300指数数据成功")
                else:
                    print("无法获取沪深300指数数据，使用默认市场状态")
        except Exception as e:
            print(f"初始化沪深300指数数据失败: {e}")
    
    def next(self):
        # 计算总资产 = 可用现金 + 持仓市值
        available_cash = self.broker.getcash()
        position_value = self.broker.getvalue() - available_cash
        total_assets = available_cash + position_value
        
        self.equity_curve.append({
            'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
            'value': total_assets
        })
        
        # 基于沪深300指数120日均线判断市场状态
        self.previous_market_state = self.market_state
        
        # 只使用统一的沪深300指数数据判断市场状态
        if BaseStrategy.hs300_df is not None:
            # 获取当前日期
            current_date = self.data.datetime.date(0)
            
            try:
                # 查找当前日期的沪深300指数数据
                # 将current_date转换为datetime对象进行查找
                current_datetime = pd.Timestamp(current_date)
                
                if current_datetime in BaseStrategy.hs300_df.index:
                    row = BaseStrategy.hs300_df.loc[current_datetime]
                    if not pd.isna(row['ma120']):
                        # 当沪深300指数价格在120日移动平均线之上时为牛市，之下时为熊市
                        if row['close'] > row['ma120']:
                            self.market_state = '牛'
                        else:
                            self.market_state = '熊'
                    else:
                        # 移动平均线数据不足时保持默认状态
                        self.market_state = '熊'
                else:
                    # 没有当前日期的数据时，尝试查找最接近的日期
                    # 将索引转换为date对象进行比较
                    index_dates = BaseStrategy.hs300_df.index.date
                    closest_idx = min(range(len(index_dates)), key=lambda i: abs(index_dates[i] - current_date))
                    closest_datetime = BaseStrategy.hs300_df.index[closest_idx]
                    row = BaseStrategy.hs300_df.loc[closest_datetime]
                    if not pd.isna(row['ma120']):
                        if row['close'] > row['ma120']:
                            self.market_state = '牛'
                        else:
                            self.market_state = '熊'
                    else:
                        self.market_state = '熊'
            except Exception as e:
                print(f"计算市场状态失败: {e}")
                # 失败时保持默认状态
                self.market_state = '熊'
        else:
            # 没有沪深300指数数据时，保持默认状态
            print("没有沪深300指数数据，使用默认熊市状态")
            self.market_state = '熊'
        
        # 当市场由牛转熊时，卖出持仓各股的八分之五
        if self.previous_market_state == '牛' and self.market_state == '熊' and self.position:
            sell_size = int(self.position.size * 5 / 8)
            # 调整为100的整数倍（向下取整）
            sell_size = (sell_size // 100) * 100
            if sell_size > 0:
                self.sell(size=sell_size)
                # 计算收益
                sell_amount = self.data.close[0] * sell_size
                buy_amount = self.buy_price * sell_size
                profit = sell_amount - buy_amount
                self.trade_log.append({
                    'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                    'symbol': self.data._name,
                    'type': 'sell',
                    'price': self.data.close[0],
                    'quantity': sell_size,
                    'profit': profit,
                    'reason': '市场由牛转熊'
                })
    
    def calculate_max_position_size(self, price):
        """计算单只股票的最大持仓数量（100的整数倍，符合1手=100股的交易规则）"""
        # 获取初始现金（在多股票回测中已设置为总初始资金的20%）
        initial_cash = self.broker.startingcash
        
        # 根据市场状态确定仓位比例
        market_position_pct = 0.8 if self.market_state == '牛' else 0.3
        
        # 购买资金 = 初始现金 × 市场仓位比例
        buy_cash = initial_cash * market_position_pct
        max_size = int(buy_cash / price)
        
        # 调整为100的整数倍（向下取整，确保不超过可用资金）
        max_size = (max_size // 100) * 100
        
        return max_size

class MovingAverageStrategy(BaseStrategy):
    params = (
        ('fast_period', 5),
        ('slow_period', 20),
        ('position_pct', 0.2),
        ('initial_cash', 1000000),  # 初始资金
    )
    
    def __init__(self):
        super().__init__()
        self.sma_fast = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.fast_period)
        self.sma_slow = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.slow_period)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)
    
    def next(self):
        # 调用基类的next方法，处理市场状态变化和总资产计算
        super().next()
        
        # 计算总资产
        available_cash = self.broker.getcash()
        position_value = self.broker.getvalue() - available_cash
        total_assets = available_cash + position_value
        
        if not self.position:
            if self.crossover > 0:
                # 计算单只股票的最大持仓数量
                size = self.calculate_max_position_size(self.data.close[0])
                
                if size > 0:
                    self.buy(size=size)
                    self.buy_price = self.data.close[0]  # 记录买入价格
                    self.buy_quantity = size  # 记录买入数量
                    self.trade_log.append({
                        'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                        'symbol': self.data._name,
                        'type': 'buy',
                        'price': self.data.close[0],
                        'quantity': size,
                        'market_state': self.market_state
                    })
        else:
            if self.crossover < 0:
                self.sell(size=self.position.size)
                # 计算收益：卖出金额 - 买入金额
                sell_amount = self.data.close[0] * self.position.size
                buy_amount = self.buy_price * self.buy_quantity
                profit = sell_amount - buy_amount
                self.trade_log.append({
                    'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                    'symbol': self.data._name,
                    'type': 'sell',
                    'price': self.data.close[0],
                    'quantity': self.position.size,
                    'profit': profit,
                    'market_state': self.market_state
                })

class MeanReversionStrategy(BaseStrategy):
    params = (
        ('period', 20),
        ('std_dev', 2),
        ('position_pct', 0.2),
        ('initial_cash', 1000000),  # 初始资金
    )
    
    def __init__(self):
        super().__init__()
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.period)
        self.std = bt.indicators.StandardDeviation(self.data.close, period=self.p.period)
        self.upper_band = self.sma + self.std * self.p.std_dev
        self.lower_band = self.sma - self.std * self.p.std_dev
    
    def next(self):
        # 调用基类的next方法，处理市场状态变化和总资产计算
        super().next()
        
        # 计算总资产
        available_cash = self.broker.getcash()
        position_value = self.broker.getvalue() - available_cash
        total_assets = available_cash + position_value
        
        if not self.position:
            if self.data.close[0] < self.lower_band[0]:
                # 计算单只股票的最大持仓数量
                size = self.calculate_max_position_size(self.data.close[0])
                
                if size > 0:
                    self.buy(size=size)
                    self.buy_price = self.data.close[0]  # 记录买入价格
                    self.buy_quantity = size  # 记录买入数量
                    self.trade_log.append({
                        'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                        'symbol': self.data._name,
                        'type': 'buy',
                        'price': self.data.close[0],
                        'quantity': size,
                        'market_state': self.market_state
                    })
        else:
            if self.data.close[0] > self.sma[0]:
                self.sell(size=self.position.size)
                # 计算收益：卖出金额 - 买入金额
                sell_amount = self.data.close[0] * self.position.size
                buy_amount = self.buy_price * self.buy_quantity
                profit = sell_amount - buy_amount
                self.trade_log.append({
                    'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                    'symbol': self.data._name,
                    'type': 'sell',
                    'price': self.data.close[0],
                    'quantity': self.position.size,
                    'profit': profit,
                    'market_state': self.market_state
                })

class MomentumStrategy(BaseStrategy):
    params = (
        ('period', 20),
        ('position_pct', 0.2),
        ('initial_cash', 1000000),  # 初始资金
    )
    
    def __init__(self):
        super().__init__()
        self.returns = bt.indicators.RateOfChange(self.data.close, period=self.p.period)
    
    def next(self):
        # 调用基类的next方法，处理市场状态变化和总资产计算
        super().next()
        
        # 计算总资产
        available_cash = self.broker.getcash()
        position_value = self.broker.getvalue() - available_cash
        total_assets = available_cash + position_value
        
        if not self.position:
            if self.returns[0] > 0:
                # 计算单只股票的最大持仓数量
                size = self.calculate_max_position_size(self.data.close[0])
                
                if size > 0:
                    self.buy(size=size)
                    self.buy_price = self.data.close[0]  # 记录买入价格
                    self.buy_quantity = size  # 记录买入数量
                    self.trade_log.append({
                        'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                        'symbol': self.data._name,
                        'type': 'buy',
                        'price': self.data.close[0],
                        'quantity': size,
                        'market_state': self.market_state
                    })
        else:
            if self.returns[0] < 0:
                self.sell(size=self.position.size)
                # 计算收益：卖出金额 - 买入金额
                sell_amount = self.data.close[0] * self.position.size
                buy_amount = self.buy_price * self.buy_quantity
                profit = sell_amount - buy_amount
                self.trade_log.append({
                    'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                    'symbol': self.data._name,
                    'type': 'sell',
                    'price': self.data.close[0],
                    'quantity': self.position.size,
                    'profit': profit,
                    'market_state': self.market_state
                })

class BreakoutStrategy(BaseStrategy):
    params = (
        ('period', 20),
        ('position_pct', 0.2),
        ('initial_cash', 1000000),  # 初始资金
    )
    
    def __init__(self):
        super().__init__()
        self.high = bt.indicators.Highest(self.data.high, period=self.p.period)
        self.low = bt.indicators.Lowest(self.data.low, period=self.p.period)
    
    def next(self):
        # 调用基类的next方法，处理市场状态变化和总资产计算
        super().next()
        
        # 计算总资产
        available_cash = self.broker.getcash()
        position_value = self.broker.getvalue() - available_cash
        total_assets = available_cash + position_value
        
        if not self.position:
            if self.data.close[0] > self.high[0]:
                # 计算单只股票的最大持仓数量
                size = self.calculate_max_position_size(self.data.close[0])
                
                if size > 0:
                    self.buy(size=size)
                    self.buy_price = self.data.close[0]  # 记录买入价格
                    self.buy_quantity = size  # 记录买入数量
                    self.trade_log.append({
                        'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                        'symbol': self.data._name,
                        'type': 'buy',
                        'price': self.data.close[0],
                        'quantity': size,
                        'market_state': self.market_state
                    })
        else:
            if self.data.close[0] < self.low[0]:
                self.sell(size=self.position.size)
                # 计算收益：卖出金额 - 买入金额
                sell_amount = self.data.close[0] * self.position.size
                buy_amount = self.buy_price * self.buy_quantity
                profit = sell_amount - buy_amount
                self.trade_log.append({
                    'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                    'symbol': self.data._name,
                    'type': 'sell',
                    'price': self.data.close[0],
                    'quantity': self.position.size,
                    'profit': profit,
                    'market_state': self.market_state
                })

class NiuHuicaiStrategy(BaseStrategy):
    params = (
        ('position_pct', 0.2),
        ('stop_loss_pct', -0.04),  # 止损4%
        ('take_profit_pct', 0.1),  # 止盈10%
        ('initial_cash', 1000000),  # 初始资金
    )
    
    def __init__(self):
        super().__init__()
        # 基础条件指标
        self.year_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=250)
        self.v_ma5 = bt.indicators.SimpleMovingAverage(self.data.volume, period=5)
        self.v_ma60 = bt.indicators.SimpleMovingAverage(self.data.volume, period=60)
        self.ma20 = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
    
    def next(self):
        try:
            # 调用基类的next方法，处理市场状态变化和总资产计算
            super().next()
            
            # 计算总资产
            available_cash = self.broker.getcash()
            position_value = self.broker.getvalue() - available_cash
            total_assets = available_cash + position_value
            
            # 检查数据有效性
            if not self.data.close[0] or not self.data.volume[0]:
                return
            
            # 检查指标有效性
            try:
                # 确保所有指标值都是有效的
                if not all([self.year_ma[0], self.v_ma5[0], self.v_ma60[0], self.ma20[0]]):
                    return
                
                # 确保所有指标值都是正数
                if any(ma <= 0 for ma in [self.year_ma[0], self.v_ma5[0], self.v_ma60[0], self.ma20[0]]):
                    return
            except Exception as e:
                print(f"指标访问错误: {e}")
                return
            
            # 基础条件：股价在年线之上 AND 5日均量大于60日均量
            try:
                base_condition = self.data.close[0] > self.year_ma[0] and self.v_ma5[0] > self.v_ma60[0]
            except Exception as e:
                print(f"基础条件计算错误: {e}")
                return
            
            if not self.position:
                # 信号条件：缩量回踩20日线
                try:
                    # 缩量：今日成交量小于5日均量的80%
                    shrink_volume = self.data.volume[0] < self.v_ma5[0] * 0.8
                    # 回踩20线：收盘价在20日均线上下1.5%范围内
                    backtest_ma20 = abs(self.data.close[0] / self.ma20[0] - 1) < 0.015
                    
                    signal = shrink_volume and backtest_ma20
                except Exception as e:
                    print(f"信号条件计算错误: {e}")
                    return
                
                if base_condition and signal:
                    try:
                        # 计算单只股票的最大持仓数量
                        size = self.calculate_max_position_size(self.data.close[0])
                        
                        if size > 0:
                            self.buy(size=size)
                            self.buy_price = self.data.close[0]  # 记录买入价格
                            self.buy_quantity = size  # 记录买入数量
                            self.trade_log.append({
                                'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                                'symbol': self.data._name,
                                'type': 'buy',
                                'price': self.data.close[0],
                                'quantity': size,
                                'market_state': self.market_state
                            })
                    except Exception as e:
                        print(f"买入操作错误: {e}")
                        return
            else:
                # 止损和止盈条件
                try:
                    # 止损：股价跌破买入价的-4%
                    if self.buy_price > 0 and self.data.close[0] < self.buy_price * (1 + self.p.stop_loss_pct):
                        self.sell(size=self.position.size)
                        # 计算收益：卖出金额 - 买入金额
                        sell_amount = self.data.close[0] * self.position.size
                        buy_amount = self.buy_price * self.buy_quantity
                        profit = sell_amount - buy_amount
                        self.trade_log.append({
                            'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                            'symbol': self.data._name,
                            'type': 'sell',
                            'price': self.data.close[0],
                            'quantity': self.position.size,
                            'profit': profit,
                            'market_state': self.market_state
                        })
                    # 止盈：达到10%
                    elif self.buy_price > 0 and self.data.close[0] > self.buy_price * (1 + self.p.take_profit_pct):
                        self.sell(size=self.position.size)
                        # 计算收益：卖出金额 - 买入金额
                        sell_amount = self.data.close[0] * self.position.size
                        buy_amount = self.buy_price * self.buy_quantity
                        profit = sell_amount - buy_amount
                        self.trade_log.append({
                            'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                            'symbol': self.data._name,
                            'type': 'sell',
                            'price': self.data.close[0],
                            'quantity': self.position.size,
                            'profit': profit,
                            'market_state': self.market_state
                        })
                except Exception as e:
                    print(f"卖出操作错误: {e}")
                    return
        except Exception as e:
            # 捕获异常，避免因指标计算错误导致回测失败
            print(f"牛回踩策略执行错误: {e}")
            import traceback
            traceback.print_exc()
            return

class BacktestEngine:
    def __init__(self, initial_cash=1000000):
        self.initial_cash = initial_cash
        self.results = {}
    
    def prepare_data(self, symbol, start_date, end_date):
        try:
            df = DataProvider.get_kline_data(symbol, start_date, end_date)
            if df is not None and not df.empty:
                return df
        except Exception as e:
            print(f"准备数据失败 {symbol}: {e}")
        return None
    
    def run_backtest(self, symbol, start_date, end_date, fast_period=5, slow_period=20, position_pct=0.2, transaction_cost=0.0003, stock_initial_cash=None, strategy_type='moving_average'):
        # 使用指定的单只股票初始资金，如果没有指定则使用总初始资金
        stock_cash = stock_initial_cash if stock_initial_cash is not None else self.initial_cash
        
        # 初始化Cerebro
        cerebro = bt.Cerebro(stdstats=False)
        cerebro.broker.setcash(stock_cash)
        
        df = self.prepare_data(symbol, start_date, end_date)
        if df is None:
            return None
        
        # 只有牛回踩策略需要检查数据量（因为需要计算年线）
        if strategy_type == 'niu_huicai' and len(df) < 250:
            print(f"数据量不足，股票 {symbol} 只有 {len(df)} 天数据，无法计算年线")
            return None
        
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data, name=symbol)
        
        # 根据策略类型选择对应的策略
        if strategy_type == 'moving_average':
            cerebro.addstrategy(MovingAverageStrategy, 
                              fast_period=fast_period, 
                              slow_period=slow_period,
                              position_pct=position_pct,
                              initial_cash=stock_cash)
        elif strategy_type == 'mean_reversion':
            cerebro.addstrategy(MeanReversionStrategy, 
                              period=20, 
                              std_dev=2,
                              position_pct=position_pct,
                              initial_cash=stock_cash)
        elif strategy_type == 'momentum':
            cerebro.addstrategy(MomentumStrategy, 
                              period=20, 
                              position_pct=position_pct,
                              initial_cash=stock_cash)
        elif strategy_type == 'breakout':
            cerebro.addstrategy(BreakoutStrategy, 
                              period=20, 
                              position_pct=position_pct,
                              initial_cash=stock_cash)
        elif strategy_type == 'niu_huicai':
            cerebro.addstrategy(NiuHuicaiStrategy, 
                              position_pct=position_pct,
                              stop_loss_pct=-0.04,
                              take_profit_pct=0.1,
                              initial_cash=stock_cash)
        else:
            # 默认使用移动平均线策略
            cerebro.addstrategy(MovingAverageStrategy, 
                              fast_period=fast_period, 
                              slow_period=slow_period,
                              position_pct=position_pct,
                              initial_cash=stock_cash)
        
        cerebro.broker.setcommission(commission=transaction_cost)
        
        try:
            print(f"开始执行回测: {symbol}")
            stratruns = cerebro.run()
            print(f"cerebro.run() 执行完成，返回结果数量: {len(stratruns) if stratruns else 0}")
            
            if not stratruns:
                print(f"回测失败：cerebro.run() 返回空列表")
                return None
            
            strategy = stratruns[0]
            print(f"策略对象创建成功，类型: {type(strategy)}")
            
            # 检查策略对象属性
            print(f"策略属性检查:")
            print(f"  - 交易日志长度: {len(strategy.trade_log) if hasattr(strategy, 'trade_log') else '无'}")
            print(f"  - 权益曲线长度: {len(strategy.equity_curve) if hasattr(strategy, 'equity_curve') else '无'}")
            
            final_value = cerebro.broker.getvalue()
            print(f"最终资产价值: {final_value}")
            
            total_return = (final_value / stock_cash - 1) * 100
            print(f"总收益率: {total_return}")
            
            # 安全获取权益曲线数据
            if hasattr(strategy, 'equity_curve') and strategy.equity_curve:
                try:
                    equity_values = [e['value'] for e in strategy.equity_curve]
                    print(f"权益值数量: {len(equity_values)}")
                    peak = max(equity_values) if equity_values else stock_cash
                    trough = min(equity_values) if equity_values else stock_cash
                    max_drawdown = (peak - trough) / peak * 100 if peak > 0 else 0
                    print(f"最大回撤: {max_drawdown}")
                except Exception as e:
                    print(f"权益曲线处理错误: {e}")
                    import traceback
                    traceback.print_exc()
                    equity_values = []
                    max_drawdown = 0
            else:
                print("无权益曲线数据")
                equity_values = []
                max_drawdown = 0
            
            # 计算日收益率
            daily_returns = []
            try:
                for i in range(1, len(equity_values)):
                    daily_returns.append((equity_values[i] - equity_values[i-1]) / equity_values[i-1])
                print(f"日收益率数量: {len(daily_returns)}")
            except Exception as e:
                print(f"日收益率计算错误: {e}")
                import traceback
                traceback.print_exc()
                daily_returns = []
            
            if daily_returns:
                try:
                    avg_return = np.mean(daily_returns) * 100
                    std_return = np.std(daily_returns) * 100
                    sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
                    print(f"夏普比率: {sharpe_ratio}")
                except Exception as e:
                    print(f"夏普比率计算错误: {e}")
                    import traceback
                    traceback.print_exc()
                    sharpe_ratio = 0
            else:
                sharpe_ratio = 0
            
            # 处理交易数据
            buy_trades = []
            sell_trades = []
            total_trades = 0
            
            if hasattr(strategy, 'trade_log'):
                try:
                    buy_trades = [t for t in strategy.trade_log if t['type'] == 'buy']
                    sell_trades = [t for t in strategy.trade_log if t['type'] == 'sell']
                    total_trades = len(strategy.trade_log)
                    print(f"交易数据: 买入{len(buy_trades)}次, 卖出{len(sell_trades)}次, 总计{total_trades}次")
                except Exception as e:
                    print(f"交易数据处理错误: {e}")
                    import traceback
                    traceback.print_exc()
            
            profit_trades = 0
            total_profit = 0
            total_loss = 0
            
            try:
                for i, sell_trade in enumerate(sell_trades):
                    if i < len(buy_trades):
                        buy_trade = buy_trades[i]
                        profit = (sell_trade['price'] - buy_trade['price']) * sell_trade['quantity']
                        if profit > 0:
                            profit_trades += 1
                            total_profit += profit
                        else:
                            total_loss += abs(profit)
                print(f"盈利交易: {profit_trades}次, 总盈利: {total_profit}, 总亏损: {total_loss}")
            except Exception as e:
                print(f"交易盈亏计算错误: {e}")
                import traceback
                traceback.print_exc()
            
            completed_trades = len(sell_trades)
            win_rate = (profit_trades / completed_trades * 100) if completed_trades > 0 else 0
            avg_profit = (total_profit / profit_trades) if profit_trades > 0 else 0
            avg_loss = (total_loss / (completed_trades - profit_trades)) if (completed_trades - profit_trades) > 0 else 0
            
            result = {
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'initial_cash': stock_cash,
                'final_value': final_value,
                'total_return': round(total_return, 2),
                'max_drawdown': round(max_drawdown, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'total_trades': total_trades,
                'win_rate': round(win_rate, 2),
                'avg_profit': round(avg_profit, 2),
                'avg_loss': round(avg_loss, 2),
                'equity_curve': strategy.equity_curve if hasattr(strategy, 'equity_curve') else [],
                'trade_log': strategy.trade_log if hasattr(strategy, 'trade_log') else []
            }
            
            print(f"回测完成，返回结果: {result}")
            return result
        except IndexError as e:
            print(f"数组索引错误: {e}")
            import traceback
            traceback.print_exc()
            return None
        except Exception as e:
            print(f"回测执行错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_multi_stock_backtest(self, symbols, start_date, end_date, fast_period=5, slow_period=20, initial_cash=1000000, transaction_cost=0.0003, strategy_type='moving_average'):
        results = []
        print(f"开始多股票回测，股票列表: {symbols}")
        print(f"回测参数: initial_cash={initial_cash}, transaction_cost={transaction_cost}, strategy_type={strategy_type}")
        
        # 计算每只股票的初始资金，每只股票分配总初始资金的20%
        per_stock_initial_cash = initial_cash * 0.2
        print(f"每只股票初始资金: {per_stock_initial_cash}")
        
        # 更新初始资金
        original_initial_cash = self.initial_cash
        self.initial_cash = initial_cash
        
        for symbol in symbols:
            print(f"正在回测股票: {symbol}")
            result = self.run_backtest(
                symbol, 
                start_date, 
                end_date, 
                fast_period=fast_period, 
                slow_period=slow_period, 
                transaction_cost=transaction_cost,
                stock_initial_cash=per_stock_initial_cash,  # 传递单只股票初始资金
                strategy_type=strategy_type  # 传递策略类型
            )
            if result:
                print(f"股票 {symbol} 回测成功")
                # 更新回测结果中的初始资金为单只股票的初始资金
                result['initial_cash'] = per_stock_initial_cash
                results.append(result)
            else:
                print(f"股票 {symbol} 回测失败或无数据，创建占位符结果")
                # 为失败的股票创建占位符结果
                results.append({
                    'symbol': symbol,
                    'start_date': start_date,
                    'end_date': end_date,
                    'initial_cash': per_stock_initial_cash,  # 使用单只股票初始资金
                    'final_value': per_stock_initial_cash,
                    'total_return': 0,
                    'max_drawdown': 0,
                    'sharpe_ratio': 0,
                    'total_trades': 0,
                    'win_rate': 0,
                    'avg_profit': 0,
                    'avg_loss': 0,
                    'equity_curve': [{'date': start_date, 'value': per_stock_initial_cash}],
                    'trade_log': []
                })
        
        # 恢复原始初始资金
        self.initial_cash = original_initial_cash
        
        print(f"处理后的股票数量: {len(results)}/{len(symbols)}")
        
        if not results:
            return None
        
        total_initial = sum(r['initial_cash'] for r in results)
        total_final = sum(r['final_value'] for r in results)
        total_return = (total_final / total_initial - 1) * 100
        
        all_equity = []
        for result in results:
            for point in result['equity_curve']:
                all_equity.append(point)
        
        all_equity_sorted = sorted(all_equity, key=lambda x: x['date'])
        equity_values = [e['value'] for e in all_equity_sorted]
        
        peak = max(equity_values) if equity_values else total_initial
        trough = min(equity_values) if equity_values else total_initial
        max_drawdown = (peak - trough) / peak * 100 if peak > 0 else 0
        
        total_trades = sum(r['total_trades'] for r in results)
        total_profit_trades = sum(r['total_trades'] * r['win_rate'] / 100 for r in results)
        win_rate = (total_profit_trades / total_trades * 100) if total_trades > 0 else 0
        
        # 构建按股票代码组织的权益曲线
        equity_curve_by_stock = {}
        for result in results:
            symbol = result['symbol']
            equity_curve_by_stock[symbol] = result['equity_curve']
        
        portfolio_result = {
            'symbols': symbols,
            'start_date': start_date,
            'end_date': end_date,
            'initial_cash': total_initial,
            'final_value': total_final,
            'total_return': round(total_return, 2),
            'max_drawdown': round(max_drawdown, 2),
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'individual_results': results,
            'equity_curve': equity_curve_by_stock
        }
        
        return portfolio_result