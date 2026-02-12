#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import efinance as ef
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

try:
    import baostock as bs
    BAOSTOCK_AVAILABLE = True
except ImportError:
    BAOSTOCK_AVAILABLE = False
    print("未安装baostock，无法使用该数据源")

try:
    import akshare as ak
    AK_SHARE_AVAILABLE = True
except ImportError:
    AK_SHARE_AVAILABLE = False
    print("未安装akshare，无法使用该数据源")

try:
    import tushare as ts
    TSHARE_AVAILABLE = True
    # 初始化tushare，这里需要用户自己设置token
    # ts.set_token('your_token_here')
    # pro = ts.pro_api()
except ImportError:
    TSHARE_AVAILABLE = False
    print("未安装tushare，无法使用该数据源")

except Exception as e:
    TSHARE_AVAILABLE = False
    print(f"tushare初始化失败: {e}")

try:
    import adata
    ADATA_AVAILABLE = True
except ImportError:
    ADATA_AVAILABLE = False
    print("未安装adata，无法使用该数据源")

class DataProvider:
    @staticmethod
    def is_a_stock(symbol):
        return symbol.isdigit() and len(symbol) == 6
    
    @staticmethod
    def is_us_stock(symbol):
        return '.' in symbol or len(symbol) <= 5
    
    @staticmethod
    def get_kline_data(symbol, start_date, end_date, adjust="qfq"):
        try:
            # 特殊处理沪深300指数
            if symbol == '399300':
                df = DataProvider._get_index_kline(symbol, start_date, end_date)
            # 验证股票代码格式
            elif not DataProvider.is_a_stock(symbol) and not DataProvider.is_us_stock(symbol):
                return None
            
            elif DataProvider.is_a_stock(symbol):
                df = DataProvider._get_a_stock_kline(symbol, start_date, end_date, adjust)
            elif DataProvider.is_us_stock(symbol):
                df = DataProvider._get_us_stock_kline(symbol, start_date, end_date)
            else:
                return None
            
            # 确保只返回数值列
            if df is not None and not df.empty:
                # 只保留数值列
                numeric_df = df.select_dtypes(include=['int64', 'float64'])
                
                # 确保有足够的数值列
                if numeric_df.empty:
                    return None
                
                # 确保所有列都是数值类型
                for col in numeric_df.columns:
                    numeric_df[col] = pd.to_numeric(numeric_df[col], errors='coerce')
                
                # 移除含有NaN的行
                numeric_df = numeric_df.dropna()
                
                if numeric_df.empty:
                    return None
                
                return numeric_df
            return None
        except Exception as e:
            print(f"获取K线数据失败 ({symbol}): {e}")
            return None
    
    @staticmethod
    def _get_a_stock_kline(symbol, start_date, end_date, adjust="qfq"):
        # 转换股票代码为baostock格式
        bs_symbol = f"sh.{symbol}" if symbol.startswith('6') else f"sz.{symbol}"
        
        # 优先使用baostock获取数据
        if BAOSTOCK_AVAILABLE:
            try:
                lg = bs.login()
                if lg.error_code == '0':
                    # 转换日期格式为YYYY-MM-DD
                    start_date_fmt = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
                    end_date_fmt = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
                    
                    rs = bs.query_history_k_data_plus(
                        bs_symbol,
                        "date,open,high,low,close,volume",
                        start_date=start_date_fmt,
                        end_date=end_date_fmt,
                        frequency="d",
                        adjustflag="3"
                    )
                    
                    if rs.error_code == '0':
                        data_list = []
                        while (rs.error_code == '0') & rs.next():
                            data_list.append(rs.get_row_data())
                        
                        if data_list:
                            df = pd.DataFrame(data_list, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                            df["datetime"] = pd.to_datetime(df["datetime"])
                            df.set_index("datetime", inplace=True)
                            
                            # 确保数值列是数值类型
                            numeric_cols = ['open', 'close', 'high', 'low', 'volume']
                            for col in numeric_cols:
                                df[col] = pd.to_numeric(df[col], errors='coerce')
                            
                            print(f"baostock成功获取K线数据 ({symbol}): {len(df)}条")
                            bs.logout()
                            return df
                    
                    bs.logout()
            except Exception as e:
                print(f"baostock获取A股K线数据失败 ({symbol}): {e}")
        
        # 尝试使用efinance获取数据
        try:
            # 确保日期格式为YYYYMMDD
            start_date_str = start_date
            end_date_str = end_date
            
            result = ef.stock.get_quote_history(
                stock_codes=[symbol], 
                beg=start_date_str, 
                end=end_date_str,
                klt=101
            )
            
            if result is not None and result:
                # 遍历result中的所有key，找到对应的DataFrame
                for key, df in result.items():
                    if df is not None and not df.empty:
                        # 清理列名中的所有类型空格
                        df.columns = df.columns.str.replace(r'\s+', '', regex=True)
                        
                        # 只选择需要的列，忽略其他列
                        selected_columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量']
                        available_columns = [col for col in selected_columns if col in df.columns]
                        if len(available_columns) >= 6:
                            # 只选择可用的列
                            df_selected = df[available_columns].copy()
                            # 重命名列
                            rename_map = {
                                "日期": "datetime",
                                "开盘": "open",
                                "最高": "high",
                                "最低": "low",
                                "收盘": "close",
                                "成交量": "volume"
                            }
                            df_selected = df_selected.rename(columns={k: v for k, v in rename_map.items() if k in df_selected.columns})
                            
                            # 确保所有需要的列都存在
                            required_cols = ['datetime', 'open', 'close', 'high', 'low', 'volume']
                            if not all(col in df_selected.columns for col in required_cols):
                                continue
                            
                            # 转换日期列
                            df_selected["datetime"] = pd.to_datetime(df_selected["datetime"])
                            df_selected.set_index("datetime", inplace=True)
                            
                            # 确保数值列是数值类型
                            numeric_cols = ['open', 'close', 'high', 'low', 'volume']
                            for col in numeric_cols:
                                if col in df_selected.columns:
                                    df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')
                            
                            # 确保所有数值列都是数值类型
                            if all(pd.api.types.is_numeric_dtype(df_selected[col]) for col in numeric_cols):
                                return df_selected
                # 如果没有找到合适的DataFrame，返回None
                print(f"无法从efinance返回结果中获取有效的K线数据 ({symbol})")
                return None
        except Exception as e:
            print(f"efinance获取A股K线数据失败 ({symbol}): {e}")
        
        # 尝试使用akshare获取数据
        if AK_SHARE_AVAILABLE:
            try:
                # 转换日期格式为YYYY-MM-DD
                start_date_fmt = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
                end_date_fmt = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
                
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_date_fmt,
                    end_date=end_date_fmt,
                    adjust=adjust
                )
                
                if df is not None and not df.empty:
                    # 只保留需要的列
                    df = df[["日期", "开盘", "收盘", "最高", "最低", "成交量"]].copy()
                    
                    # 重命名列并设置索引
                    df.rename(columns={
                        "日期": "datetime",
                        "开盘": "open",
                        "最高": "high",
                        "最低": "low",
                        "收盘": "close",
                        "成交量": "volume"
                    }, inplace=True)
                    
                    df["datetime"] = pd.to_datetime(df["datetime"])
                    df.set_index("datetime", inplace=True)
                    
                    # 确保数值列是数值类型
                    numeric_cols = ['open', 'close', 'high', 'low', 'volume']
                    for col in numeric_cols:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    return df
            except Exception as e:
                print(f"akshare获取A股K线数据失败 ({symbol}): {e}")
        
        # 尝试使用tushare获取数据
        if TSHARE_AVAILABLE:
            try:
                # 注意：tushare需要设置token才能使用
                # 转换日期格式为YYYYMMDD
                start_date_fmt = start_date
                end_date_fmt = end_date
                
                # 使用tushare获取数据
                df = ts.pro_bar(
                    ts_code=f"{symbol}.SZ" if symbol.startswith('0') or symbol.startswith('3') else f"{symbol}.SH",
                    adj=adjust,
                    start_date=start_date_fmt,
                    end_date=end_date_fmt
                )
                
                if df is not None and not df.empty:
                    # 重命名列并设置索引
                    df.rename(columns={
                        "trade_date": "datetime",
                        "open": "open",
                        "high": "high",
                        "low": "low",
                        "close": "close",
                        "vol": "volume"
                    }, inplace=True)
                    
                    # 转换日期格式
                    df["datetime"] = pd.to_datetime(df["datetime"])
                    df.set_index("datetime", inplace=True)
                    
                    # 按日期排序
                    df.sort_index(inplace=True)
                    
                    # 确保数值列是数值类型
                    numeric_cols = ['open', 'close', 'high', 'low', 'volume']
                    for col in numeric_cols:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    return df
            except Exception as e:
                print(f"tushare获取A股K线数据失败 ({symbol}): {e}")
        
        print(f"所有数据源均无法获取股票 {symbol} 的K线数据")
        return None
    
    @staticmethod
    def _get_us_stock_kline(symbol, start_date, end_date):
        try:
            start_date_str = start_date[:4] + '-' + start_date[4:6] + '-' + start_date[6:8]
            end_date_str = end_date[:4] + '-' + end_date[4:6] + '-' + end_date[6:8]
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date_str, end=end_date_str)
            
            if df is None or df.empty:
                return None
            
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df.rename(columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume"
            }, inplace=True)
            
            df.index.name = "datetime"
            
            return df
        except Exception as e:
            print(f"获取美股K线数据失败 ({symbol}): {e}")
            return None
    
    @staticmethod
    def download_hs300_data():
        """从efinance下载5年内的沪深300指数数据"""
        try:
            # 计算5年前的日期
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365*5)
            
            # 转换为YYYYMMDD格式
            start_date_str = start_date.strftime('%Y%m%d')
            end_date_str = end_date.strftime('%Y%m%d')
            
            # 使用efinance获取沪深300指数数据
            print(f"开始下载沪深300指数数据 (2021-2026)")
            result = ef.stock.get_quote_history(
                stock_codes=['399300'], 
                beg=start_date_str, 
                end=end_date_str,
                klt=101  # 日K线
            )
            
            if result is not None and result:
                # 遍历result中的所有key，找到对应的DataFrame
                for key, df in result.items():
                    if df is not None and not df.empty:
                        # 清理列名中的所有类型空格
                        df.columns = df.columns.str.replace(r'\s+', '', regex=True)
                        
                        # 只选择需要的列，忽略其他列
                        selected_columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量']
                        available_columns = [col for col in selected_columns if col in df.columns]
                        if len(available_columns) >= 6:
                            # 只选择可用的列
                            df_selected = df[available_columns].copy()
                            # 重命名列
                            rename_map = {
                                "日期": "datetime",
                                "开盘": "open",
                                "最高": "high",
                                "最低": "low",
                                "收盘": "close",
                                "成交量": "volume"
                            }
                            df_selected = df_selected.rename(columns={k: v for k, v in rename_map.items() if k in df_selected.columns})
                            
                            # 确保所有需要的列都存在
                            required_cols = ['datetime', 'open', 'close', 'high', 'low', 'volume']
                            if not all(col in df_selected.columns for col in required_cols):
                                continue
                            
                            # 转换日期列
                            df_selected["datetime"] = pd.to_datetime(df_selected["datetime"])
                            df_selected.set_index("datetime", inplace=True)
                            
                            # 确保数值列是数值类型
                            numeric_cols = ['open', 'close', 'high', 'low', 'volume']
                            for col in numeric_cols:
                                if col in df_selected.columns:
                                    df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')
                            
                            # 确保所有数值列都是数值类型
                            if all(pd.api.types.is_numeric_dtype(df_selected[col]) for col in numeric_cols):
                                # 计算120日移动平均线
                                df_selected['ma120'] = df_selected['close'].rolling(window=120).mean()
                                print(f"成功从efinance获取沪深300指数数据 ({len(df_selected)} 条记录)")
                                return df_selected
                # 如果没有找到合适的DataFrame，返回None
                print("无法从efinance返回结果中获取有效的沪深300指数数据")
                return None
        except Exception as e:
            print(f"下载沪深300指数数据失败: {e}")
            return None
    
    @staticmethod
    def save_hs300_data(df):
        """将沪深300指数数据保存到本地文件"""
        try:
            # 创建数据目录（如果不存在）
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"创建数据目录: {data_dir}")
            
            # 保存为CSV文件
            file_path = os.path.join(data_dir, 'hs300_data.csv')
            df.to_csv(file_path)
            print(f"成功将沪深300指数数据保存到: {file_path}")
            return file_path
        except Exception as e:
            print(f"保存沪深300指数数据失败: {e}")
            return None
    
    @staticmethod
    def load_hs300_data():
        """从本地文件加载沪深300指数数据"""
        try:
            # 数据文件路径
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            file_path = os.path.join(data_dir, 'hs300_data.csv')
            
            if os.path.exists(file_path):
                # 读取CSV文件
                df = pd.read_csv(file_path, index_col='datetime', parse_dates=True)
                print(f"成功从本地文件加载沪深300指数数据 ({len(df)} 条记录)")
                return df
            else:
                print(f"沪深300指数数据文件不存在: {file_path}")
                return None
        except Exception as e:
            print(f"加载沪深300指数数据失败: {e}")
            return None
    
    @staticmethod
    def update_hs300_data():
        """更新沪深300指数数据"""
        try:
            # 下载最新数据
            df = DataProvider.download_hs300_data()
            if df is not None and not df.empty:
                # 保存到本地文件
                file_path = DataProvider.save_hs300_data(df)
                if file_path:
                    print("沪深300指数数据更新成功")
                    return True
            print("沪深300指数数据更新失败")
            return False
        except Exception as e:
            print(f"更新沪深300指数数据失败: {e}")
            return False
    
    @staticmethod
    def _get_index_kline(symbol, start_date, end_date):
        # 尝试使用akshare获取指数数据
        if AK_SHARE_AVAILABLE:
            try:
                # 转换日期格式为YYYY-MM-DD
                start_date_str = start_date[:4] + '-' + start_date[4:6] + '-' + start_date[6:8]
                end_date_str = end_date[:4] + '-' + end_date[4:6] + '-' + end_date[6:8]
                
                # 尝试使用akshare的指数数据接口
                df = ak.stock_zh_index_daily_em(
                    symbol=symbol,
                    start_date=start_date_str,
                    end_date=end_date_str
                )
                
                if df is not None and not df.empty:
                    # 只保留需要的列
                    df = df[["日期", "开盘", "收盘", "最高", "最低", "成交量"]].copy()
                    
                    # 重命名列并设置索引
                    df.rename(columns={
                        "日期": "datetime",
                        "开盘": "open",
                        "最高": "high",
                        "最低": "low",
                        "收盘": "close",
                        "成交量": "volume"
                    }, inplace=True)
                    
                    df["datetime"] = pd.to_datetime(df["datetime"])
                    df.set_index("datetime", inplace=True)
                    
                    # 确保数值列是数值类型
                    numeric_cols = ['open', 'close', 'high', 'low', 'volume']
                    for col in numeric_cols:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    print(f"成功从akshare获取指数数据 ({symbol})")
                    return df
            except Exception as e:
                print(f"akshare获取指数数据失败 ({symbol}): {e}")
        
        # 尝试使用efinance获取指数数据
        try:
            # 确保日期格式为YYYYMMDD
            start_date_str = start_date
            end_date_str = end_date
            
            result = ef.stock.get_quote_history(
                stock_codes=[symbol], 
                beg=start_date_str, 
                end=end_date_str,
                klt=101
            )
            
            if result is not None and result:
                # 遍历result中的所有key，找到对应的DataFrame
                for key, df in result.items():
                    if df is not None and not df.empty:
                        # 清理列名中的所有类型空格
                        df.columns = df.columns.str.replace(r'\s+', '', regex=True)
                        
                        # 只选择需要的列，忽略其他列
                        selected_columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量']
                        available_columns = [col for col in selected_columns if col in df.columns]
                        if len(available_columns) >= 6:
                            # 只选择可用的列
                            df_selected = df[available_columns].copy()
                            # 重命名列
                            rename_map = {
                                "日期": "datetime",
                                "开盘": "open",
                                "最高": "high",
                                "最低": "low",
                                "收盘": "close",
                                "成交量": "volume"
                            }
                            df_selected = df_selected.rename(columns={k: v for k, v in rename_map.items() if k in df_selected.columns})
                            
                            # 确保所有需要的列都存在
                            required_cols = ['datetime', 'open', 'close', 'high', 'low', 'volume']
                            if not all(col in df_selected.columns for col in required_cols):
                                continue
                            
                            # 转换日期列
                            df_selected["datetime"] = pd.to_datetime(df_selected["datetime"])
                            df_selected.set_index("datetime", inplace=True)
                            
                            # 确保数值列是数值类型
                            numeric_cols = ['open', 'close', 'high', 'low', 'volume']
                            for col in numeric_cols:
                                if col in df_selected.columns:
                                    df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')
                            
                            # 确保所有数值列都是数值类型
                            if all(pd.api.types.is_numeric_dtype(df_selected[col]) for col in numeric_cols):
                                print(f"成功从efinance获取指数数据 ({symbol})")
                                return df_selected
                # 如果没有找到合适的DataFrame，返回None
                print(f"无法从efinance返回结果中获取有效的指数数据 ({symbol})")
                return None
        except Exception as e:
            print(f"efinance获取指数数据失败 ({symbol}): {e}")
        
        # 尝试从本地文件加载数据
        try:
            df = DataProvider.load_hs300_data()
            if df is not None and not df.empty:
                # 过滤日期范围
                start_date_obj = datetime.strptime(start_date, '%Y%m%d')
                end_date_obj = datetime.strptime(end_date, '%Y%m%d')
                df = df[(df.index >= start_date_obj) & (df.index <= end_date_obj)]
                if not df.empty:
                    print(f"成功从本地文件获取指数数据 ({symbol})")
                    return df
        except Exception as e:
            print(f"从本地文件获取指数数据失败 ({symbol}): {e}")
        
        # 如果所有数据源都失败，返回None
        print(f"所有数据源都失败，无法获取指数数据 ({symbol})")
        return None
    
    @staticmethod
    def get_current_price(symbol):
        try:
            print(f"[DEBUG] DataProvider.get_current_price({symbol}) 被调用")
            if DataProvider.is_a_stock(symbol):
                print(f"[DEBUG] {symbol} 是A股股票，调用 _get_a_stock_price")
                return DataProvider._get_a_stock_price(symbol)
            elif DataProvider.is_us_stock(symbol):
                print(f"[DEBUG] {symbol} 是美股股票，调用 _get_us_stock_price")
                return DataProvider._get_us_stock_price(symbol)
            else:
                print(f"[DEBUG] {symbol} 不是有效的股票代码")
                return None
        except Exception as e:
            print(f"获取当前价格失败 ({symbol}): {e}")
            return None
    
    @staticmethod
    def _get_a_stock_price(symbol):
        """获取A股当前价格，使用baostock作为第一选择，adata、akshare和efinance作为备选，带重试机制"""
        max_retries = 3
        retry_delay = 0.5  # 秒
        
        for attempt in range(max_retries):
            try:
                # 方法1: 使用baostock获取实时行情（第一选择）
                if BAOSTOCK_AVAILABLE:
                    try:
                        print(f"[DEBUG] 尝试使用baostock获取 {symbol} 的价格...")
                        lg = bs.login()
                        print(f"[DEBUG] baostock登录结果: {lg.error_code}, {lg.error_msg}")
                        if lg.error_code == '0':
                            # 获取最近一天的数据
                            end_date = datetime.now().strftime("%Y-%m-%d")
                            start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
                            print(f"[DEBUG] 查询日期范围: {start_date} 到 {end_date}")
                            
                            # 判断股票代码类型（上海或深圳）
                            if symbol.startswith('6'):
                                bs_code = f"sh.{symbol}"
                            else:
                                bs_code = f"sz.{symbol}"
                            print(f"[DEBUG] baostock代码: {bs_code}")
                            
                            rs = bs.query_history_k_data_plus(
                                bs_code,
                                "date,open,high,low,close,volume",
                                start_date=start_date,
                                end_date=end_date,
                                frequency="d",
                                adjustflag="3"
                            )
                            print(f"[DEBUG] baostock查询结果: {rs.error_code}, {rs.error_msg}")
                            
                            if rs.error_code == '0':
                                data_list = []
                                while (rs.error_code == '0') & rs.next():
                                    data_list.append(rs.get_row_data())
                                
                                print(f"[DEBUG] baostock获取到 {len(data_list)} 条数据")
                                if data_list:
                                    latest_data = data_list[-1]
                                    close_price = float(latest_data[4])
                                    print(f"[DEBUG] baostock最新数据: {latest_data}, 收盘价: {close_price}")
                                    if close_price > 0:
                                        bs.logout()
                                        print(f"baostock获取到 {symbol} 实时价格: {close_price}")
                                        return close_price
                            
                            bs.logout()
                    except Exception as e:
                        print(f"baostock获取价格失败 (尝试 {attempt+1}/{max_retries}): {e}")
                        import traceback
                        traceback.print_exc()
                
                # 方法2: 使用adata获取实时行情（备选）
                if ADATA_AVAILABLE:
                    try:
                        df = adata.stock.market.get_market()
                        if df is not None and not df.empty:
                            # 查找对应股票
                            stock_df = df[df['stock_code'] == symbol]
                            if not stock_df.empty:
                                price = float(stock_df['close'].values[0])
                                print(f"adata获取到 {symbol} 实时价格: {price}")
                                return price
                    except Exception as e:
                        print(f"adata获取价格失败 (尝试 {attempt+1}/{max_retries}): {e}")
                
                # 方法3: 使用akshare获取单个股票的实时行情（备选）
                try:
                    import akshare as ak
                    # 使用akshare的实时行情接口
                    df = ak.stock_zh_a_spot_em()
                    if df is not None and not df.empty:
                        # 查找对应股票
                        stock_df = df[df['代码'] == symbol]
                        if not stock_df.empty:
                            price = float(stock_df['最新价'].values[0])
                            print(f"akshare获取到 {symbol} 实时价格: {price}")
                            return price
                except Exception as e:
                    print(f"akshare获取价格失败 (尝试 {attempt+1}/{max_retries}): {e}")
                
                # 方法4: 使用efinance获取实时行情（备选）
                try:
                    df = ef.stock.get_realtime_quotes()
                    if df is not None and not df.empty:
                        df.columns = df.columns.str.replace(' ', '')
                        stock_df = df[df['股票代码'] == symbol]
                        if not stock_df.empty:
                            price = float(stock_df['最新价'].values[0])
                            print(f"efinance获取到 {symbol} 实时价格: {price}")
                            return price
                except Exception as e:
                    print(f"efinance获取价格失败 (尝试 {attempt+1}/{max_retries}): {e}")
                
                # 如果失败，等待后重试
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    
            except Exception as e:
                print(f"获取A股当前价格失败 (尝试 {attempt+1}/{max_retries}) ({symbol}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
        
        print(f"所有尝试都失败，无法获取 {symbol} 的实时价格")
        return None
    
    @staticmethod
    def _get_us_stock_price(symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if info and 'currentPrice' in info:
                return float(info['currentPrice'])
            elif info and 'regularMarketPrice' in info:
                return float(info['regularMarketPrice'])
            return None
        except Exception as e:
            print(f"获取美股当前价格失败 ({symbol}): {e}")
            return None
    
    @staticmethod
    def get_hs300_components():
        # 方法1: 使用adata获取股票列表（第一选择）
        if ADATA_AVAILABLE:
            try:
                df = adata.stock.market.get_market()
                if df is not None and not df.empty:
                    return df['stock_code'].tolist()[:300]
            except Exception as e:
                print(f"adata获取股票列表失败: {e}")
        
        # 方法2: 使用efinance获取股票列表（备选）
        try:
            df = ef.stock.get_realtime_quotes()
            if df is not None and not df.empty:
                # 清理列名中的空格
                df.columns = df.columns.str.replace(' ', '')
                if '股票代码' in df.columns:
                    return df['股票代码'].tolist()[:300]
        except Exception as e:
            print(f"efinance获取股票列表失败: {e}")
        
        return ['600519', '002371', '000858', '002415', '002236']
    
    @staticmethod
    def get_stock_info(symbol):
        try:
            if DataProvider.is_a_stock(symbol):
                return DataProvider._get_a_stock_info(symbol)
            elif DataProvider.is_us_stock(symbol):
                return DataProvider._get_us_stock_info(symbol)
            else:
                return None
        except Exception as e:
            print(f"获取股票信息失败 ({symbol}): {e}")
            return None
    
    @staticmethod
    def _get_a_stock_info(symbol):
        # 方法1: 使用baostock获取股票信息（第一选择）
        if BAOSTOCK_AVAILABLE:
            try:
                lg = bs.login()
                if lg.error_code == '0':
                    bs_symbol = f"sh.{symbol}" if symbol.startswith('6') else f"sz.{symbol}"
                    rs = bs.query_stock_basic(code=bs_symbol)
                    
                    if rs.error_code == '0':
                        data_list = []
                        while (rs.error_code == '0') & rs.next():
                            data_list.append(rs.get_row_data())
                        
                        if data_list:
                            bs.logout()
                            stock_name = data_list[0][1]
                            
                            # 获取实时价格
                            price_rs = bs.query_history_k_data_plus(
                                bs_symbol,
                                "open,close",
                                start_date=datetime.now().strftime('%Y-%m-%d'),
                                end_date=datetime.now().strftime('%Y-%m-%d'),
                                frequency="d",
                                adjustflag="3"
                            )
                            
                            current_price = 0
                            if price_rs.error_code == '0':
                                price_data = []
                                while (price_rs.error_code == '0') & price_rs.next():
                                    price_data.append(price_rs.get_row_data())
                                if price_data:
                                    current_price = float(price_data[0][1])
                            
                            return {
                                "symbol": symbol,
                                "name": stock_name,
                                "price": current_price,
                                "open": 0,
                                "change": 0,
                                "volume": 0,
                                "market_cap": 0
                            }
                    
                    bs.logout()
            except Exception as e:
                print(f"baostock获取股票信息失败 ({symbol}): {e}")
        
        # 方法2: 使用adata获取股票信息（备选）
        if ADATA_AVAILABLE:
            try:
                df = adata.stock.market.get_market()
                if df is not None and not df.empty:
                    stock_df = df[df['stock_code'] == symbol]
                    if not stock_df.empty:
                        return {
                            "symbol": symbol,
                            "name": "",  # adata 不提供股票名称
                            "price": float(stock_df['close'].values[0]),
                            "open": float(stock_df['open'].values[0]),
                            "change": float(stock_df['change_pct'].values[0]),
                            "volume": int(stock_df['volume'].values[0]),
                            "market_cap": 0  # adata 不提供总市值
                        }
            except Exception as e:
                print(f"adata获取股票信息失败 ({symbol}): {e}")
        
        # 方法3: 使用efinance获取股票信息（备选）
        try:
            df = ef.stock.get_realtime_quotes()
            if df is not None and not df.empty:
                df.columns = df.columns.str.replace(' ', '')
                stock_df = df[df['股票代码'] == symbol]
                if not stock_df.empty:
                    return {
                        "symbol": symbol,
                        "name": stock_df['股票名称'].values[0],
                        "price": float(stock_df['最新价'].values[0]),
                        "open": float(stock_df['今开'].values[0]) if '今开' in stock_df.columns else None,
                        "change": float(stock_df['涨跌幅'].values[0]),
                        "volume": int(stock_df['成交量'].values[0]),
                        "market_cap": float(stock_df['总市值'].values[0]) if '总市值' in stock_df.columns else 0
                    }
            return None
        except Exception as e:
            print(f"efinance获取A股股票信息失败 ({symbol}): {e}")
            return None
    
    @staticmethod
    def _get_us_stock_info(symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if info:
                current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
                previous_close = info.get('previousClose', current_price)
                change = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
                
                return {
                    "symbol": symbol,
                    "name": info.get('longName', symbol),
                    "price": float(current_price),
                    "change": float(change),
                    "volume": int(info.get('volume', 0)),
                    "market_cap": float(info.get('marketCap', 0))
                }
            return None
        except Exception as e:
            print(f"获取美股股票信息失败 ({symbol}): {e}")
            return None