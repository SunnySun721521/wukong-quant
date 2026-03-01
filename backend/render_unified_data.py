# -*- coding: utf-8 -*-
"""
Render 环境统一数据提供模块
所有数据获取功能优先使用 yfinance
与本地环境完全隔离，不影响本地程序运行
"""
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

RENDER_ENV = os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_ID')

def is_render_environment():
    """检测是否在 Render 环境"""
    return RENDER_ENV is not None


class RenderDataProvider:
    """Render 环境数据提供类"""
    
    @staticmethod
    def get_a_stock_kline(symbol, start_date, end_date):
        """
        获取A股K线数据 - Render环境优先yfinance
        
        Args:
            symbol: 股票代码 (如 600519)
            start_date: 开始日期 (YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (YYYYMMDD 或 YYYY-MM-DD)
        
        Returns:
            DataFrame with columns: open, high, low, close, volume
        """
        if not is_render_environment():
            return None
        
        # 标准化日期格式
        if len(start_date) == 8:
            start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
        if len(end_date) == 8:
            end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
        
        # 方法1: yfinance (首选)
        try:
            import yfinance as yf
            if symbol.startswith('6'):
                yf_symbol = f"{symbol}.SS"
            else:
                yf_symbol = f"{symbol}.SZ"
            
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df is not None and not df.empty:
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                df.columns = ['open', 'high', 'low', 'close', 'volume']
                df.index.name = 'datetime'
                print(f"[Render] yfinance获取A股K线成功: {symbol}, {len(df)}条")
                return df
        except Exception as e:
            print(f"[Render] yfinance获取失败: {e}")
        
        # 方法2: efinance
        try:
            import efinance as ef
            start_str = start_date.replace('-', '')
            end_str = end_date.replace('-', '')
            result = ef.stock.get_quote_history(
                stock_codes=[symbol],
                beg=start_str,
                end=end_str,
                klt=101
            )
            if result:
                for key, df in result.items():
                    if df is not None and not df.empty:
                        df.columns = df.columns.str.replace(r'\s+', '', regex=True)
                        col_map = {'日期': 'datetime', '开盘': 'open', '收盘': 'close', 
                                   '最高': 'high', '最低': 'low', '成交量': 'volume'}
                        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
                        if 'datetime' in df.columns:
                            df['datetime'] = pd.to_datetime(df['datetime'])
                            df.set_index('datetime', inplace=True)
                            print(f"[Render] efinance获取A股K线成功: {symbol}, {len(df)}条")
                            return df[['open', 'high', 'low', 'close', 'volume']]
        except Exception as e:
            print(f"[Render] efinance获取失败: {e}")
        
        # 方法3: akshare
        try:
            import akshare as ak
            import socket
            socket.setdefaulttimeout(30)
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            if df is not None and not df.empty:
                col_map = {'日期': 'datetime', '开盘': 'open', '收盘': 'close',
                           '最高': 'high', '最低': 'low', '成交量': 'volume'}
                df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
                if 'datetime' in df.columns:
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df.set_index('datetime', inplace=True)
                    print(f"[Render] akshare获取A股K线成功: {symbol}, {len(df)}条")
                    return df[['open', 'high', 'low', 'close', 'volume']]
        except Exception as e:
            print(f"[Render] akshare获取失败: {e}")
        
        # 方法4: baostock (最后备选)
        try:
            import baostock as bs
            lg = bs.login()
            if lg.error_code == '0':
                bs_code = f"sh.{symbol}" if symbol.startswith('6') else f"sz.{symbol}"
                rs = bs.query_history_k_data_plus(
                    bs_code,
                    "date,open,high,low,close,volume",
                    start_date=start_date,
                    end_date=end_date,
                    frequency="d",
                    adjustflag="3"
                )
                if rs.error_code == '0':
                    data_list = []
                    while rs.next():
                        data_list.append(rs.get_row_data())
                    if data_list:
                        df = pd.DataFrame(data_list, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                        df['datetime'] = pd.to_datetime(df['datetime'])
                        df.set_index('datetime', inplace=True)
                        for col in ['open', 'high', 'low', 'close', 'volume']:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        bs.logout()
                        print(f"[Render] baostock获取A股K线成功: {symbol}, {len(df)}条")
                        return df
                bs.logout()
        except Exception as e:
            print(f"[Render] baostock获取失败: {e}")
        
        print(f"[Render] 所有数据源均无法获取 {symbol} K线数据")
        return None
    
    @staticmethod
    def get_a_stock_price(symbol):
        """获取A股当前价格"""
        if not is_render_environment():
            return None
        
        # yfinance
        try:
            import yfinance as yf
            yf_symbol = f"{symbol}.SS" if symbol.startswith('6') else f"{symbol}.SZ"
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period="5d")
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
                print(f"[Render] yfinance获取价格: {symbol} = {price}")
                return price
        except Exception as e:
            print(f"[Render] yfinance获取价格失败: {e}")
        
        # efinance
        try:
            import efinance as ef
            df = ef.stock.get_realtime_quotes()
            if df is not None and not df.empty:
                df.columns = df.columns.str.replace(' ', '')
                stock_df = df[df['股票代码'] == symbol]
                if not stock_df.empty:
                    return float(stock_df['最新价'].values[0])
        except Exception as e:
            print(f"[Render] efinance获取价格失败: {e}")
        
        # akshare
        try:
            import akshare as ak
            import socket
            socket.setdefaulttimeout(30)
            df = ak.stock_zh_a_spot_em()
            if df is not None and not df.empty:
                stock_df = df[df['代码'] == symbol]
                if not stock_df.empty:
                    return float(stock_df['最新价'].values[0])
        except Exception as e:
            print(f"[Render] akshare获取价格失败: {e}")
        
        return None
    
    @staticmethod
    def get_stock_info(symbol):
        """获取股票基本信息"""
        if not is_render_environment():
            return None
        
        try:
            import yfinance as yf
            yf_symbol = f"{symbol}.SS" if symbol.startswith('6') else f"{symbol}.SZ"
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'industry': info.get('industry', ''),
                'sector': info.get('sector', ''),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'pb_ratio': info.get('priceToBook', 0)
            }
        except Exception as e:
            print(f"[Render] 获取股票信息失败: {e}")
            return {'symbol': symbol, 'name': symbol}
    
    @staticmethod
    def get_index_data(index_code='000300', days=120):
        """获取指数数据 (沪深300等)"""
        if not is_render_environment():
            return None, None, None, None
        
        print(f"[Render] 开始获取指数数据: {index_code}")
        
        # 方法1: yfinance - 使用正确的指数代码
        try:
            import yfinance as yf
            
            # 沪深300指数的yfinance代码映射
            index_mapping = {
                '000300': ['000300.SS', 'CSI300.SS'],  # 沪深300
                '000001': ['000001.SS', 'SSE.SS'],      # 上证指数
                '399001': ['399001.SZ', 'SZSE.SZ'],     # 深证成指
                '399006': ['399006.SZ'],                # 创业板指
            }
            
            yf_symbols = index_mapping.get(index_code, [f"{index_code}.SS"])
            
            for yf_symbol in yf_symbols:
                try:
                    print(f"[Render] 尝试yfinance代码: {yf_symbol}")
                    ticker = yf.Ticker(yf_symbol)
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days + 50)
                    hist = ticker.history(start=start_date, end=end_date)
                    
                    if not hist.empty and len(hist) > 0:
                        current_price = float(hist['Close'].iloc[-1])
                        prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                        change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                        
                        # 计算MA120
                        if len(hist) >= 120:
                            ma120 = float(hist['Close'].tail(120).mean())
                        else:
                            ma120 = float(hist['Close'].mean())
                        
                        print(f"[Render] yfinance获取指数成功 {yf_symbol}: 价格={current_price:.2f}, 涨跌={change_pct:.2f}%")
                        return current_price, change_pct, ma120, hist
                except Exception as e:
                    print(f"[Render] yfinance代码 {yf_symbol} 失败: {e}")
                    continue
        except Exception as e:
            print(f"[Render] yfinance获取指数失败: {e}")
        
        # 方法2: 使用akshare获取指数数据
        try:
            import akshare as ak
            import socket
            socket.setdefaulttimeout(30)
            
            end_date_str = datetime.now().strftime('%Y%m%d')
            start_date_str = (datetime.now() - timedelta(days=days + 50)).strftime('%Y%m%d')
            
            # akshare指数代码映射
            ak_index_map = {
                '000300': 'sh000300',   # 沪深300
                '000001': 'sh000001',   # 上证指数
                '399001': 'sz399001',   # 深证成指
                '399006': 'sz399006',   # 创业板指
            }
            
            ak_symbol = ak_index_map.get(index_code, f'sh{index_code}')
            print(f"[Render] 尝试akshare获取: {ak_symbol}")
            
            df = ak.stock_zh_index_daily(symbol=ak_symbol)
            if df is not None and not df.empty:
                # 筛选日期范围
                df['date'] = pd.to_datetime(df['date'])
                df = df[(df['date'] >= start_date_str) & (df['date'] <= end_date_str)]
                df.sort_values('date', inplace=True)
                
                if not df.empty:
                    current_price = float(df['close'].iloc[-1])
                    prev_price = float(df['close'].iloc[-2]) if len(df) > 1 else current_price
                    change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                    
                    if len(df) >= 120:
                        ma120 = float(df['close'].tail(120).mean())
                    else:
                        ma120 = float(df['close'].mean())
                    
                    # 转换为yfinance格式
                    hist = df.set_index('date')[['open', 'high', 'low', 'close', 'volume']].copy()
                    hist.index.name = 'Date'
                    
                    print(f"[Render] akshare获取指数成功: 价格={current_price:.2f}, 涨跌={change_pct:.2f}%")
                    return current_price, change_pct, ma120, hist
        except Exception as e:
            print(f"[Render] akshare获取指数失败: {e}")
        
        # 方法3: 使用efinance获取指数数据
        try:
            import efinance as ef
            
            end_date_str = datetime.now().strftime('%Y%m%d')
            start_date_str = (datetime.now() - timedelta(days=days + 50)).strftime('%Y%m%d')
            
            print(f"[Render] 尝试efinance获取指数: {index_code}")
            
            df = ef.stock.get_quote_history(
                stock_codes=[index_code],
                beg=start_date_str,
                end=end_date_str,
                klt=101
            )
            
            if df and index_code in df:
                result_df = df[index_code]
                if result_df is not None and not result_df.empty:
                    result_df.columns = result_df.columns.str.replace(r'\s+', '', regex=True)
                    col_map = {'日期': 'date', '开盘': 'open', '收盘': 'close', 
                               '最高': 'high', '最低': 'low', '成交量': 'volume'}
                    result_df = result_df.rename(columns={k: v for k, v in col_map.items() if k in result_df.columns})
                    
                    if 'date' in result_df.columns:
                        result_df['date'] = pd.to_datetime(result_df['date'])
                        result_df.sort_values('date', inplace=True)
                        
                        current_price = float(result_df['close'].iloc[-1])
                        prev_price = float(result_df['close'].iloc[-2]) if len(result_df) > 1 else current_price
                        change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                        
                        if len(result_df) >= 120:
                            ma120 = float(result_df['close'].tail(120).mean())
                        else:
                            ma120 = float(result_df['close'].mean())
                        
                        hist = result_df.set_index('date')[['open', 'high', 'low', 'close', 'volume']].copy()
                        hist.index.name = 'Date'
                        
                        print(f"[Render] efinance获取指数成功: 价格={current_price:.2f}, 涨跌={change_pct:.2f}%")
                        return current_price, change_pct, ma120, hist
        except Exception as e:
            print(f"[Render] efinance获取指数失败: {e}")
        
        # 方法4: 使用baostock获取指数数据
        try:
            import baostock as bs
            
            lg = bs.login()
            if lg.error_code == '0':
                end_date_str = datetime.now().strftime('%Y-%m-%d')
                start_date_str = (datetime.now() - timedelta(days=days + 50)).strftime('%Y-%m-%d')
                
                # baostock指数代码
                bs_code = f"sh.{index_code}" if index_code.startswith('000') else f"sz.{index_code}"
                print(f"[Render] 尝试baostock获取: {bs_code}")
                
                rs = bs.query_history_k_data_plus(
                    bs_code,
                    "date,open,high,low,close,volume",
                    start_date=start_date_str,
                    end_date=end_date_str,
                    frequency="d",
                    adjustflag="3"
                )
                
                if rs.error_code == '0':
                    data_list = []
                    while rs.next():
                        data_list.append(rs.get_row_data())
                    
                    if data_list:
                        df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                        df['date'] = pd.to_datetime(df['date'])
                        for col in ['open', 'high', 'low', 'close', 'volume']:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                        current_price = float(df['close'].iloc[-1])
                        prev_price = float(df['close'].iloc[-2]) if len(df) > 1 else current_price
                        change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                        
                        if len(df) >= 120:
                            ma120 = float(df['close'].tail(120).mean())
                        else:
                            ma120 = float(df['close'].mean())
                        
                        hist = df.set_index('date')[['open', 'high', 'low', 'close', 'volume']].copy()
                        hist.index.name = 'Date'
                        
                        bs.logout()
                        print(f"[Render] baostock获取指数成功: 价格={current_price:.2f}, 涨跌={change_pct:.2f}%")
                        return current_price, change_pct, ma120, hist
                
                bs.logout()
        except Exception as e:
            print(f"[Render] baostock获取指数失败: {e}")
        
        print(f"[Render] 所有方法均无法获取指数 {index_code} 数据")
        return None, None, None, None
    
    @staticmethod
    def get_hs300_components():
        """获取沪深300成分股列表"""
        if not is_render_environment():
            return None
        
        # 返回默认的沪深300部分成分股
        default_hs300 = [
            "600519", "002371", "000858", "002415", "002236",
            "600036", "601318", "601398", "000333", "600104",
            "600050", "601288", "600009", "600016", "600030",
            "601012", "601888", "603259", "603501", "002594",
            "000001", "300059", "600887", "601166", "600000",
            "600028", "600019", "600005", "600011", "600015"
        ]
        return default_hs300


def get_kline_data_render(symbol, start_date, end_date):
    """Render环境获取K线数据的入口函数"""
    if not is_render_environment():
        return None
    return RenderDataProvider.get_a_stock_kline(symbol, start_date, end_date)


def get_current_price_render(symbol):
    """Render环境获取当前价格的入口函数"""
    if not is_render_environment():
        return None
    return RenderDataProvider.get_a_stock_price(symbol)


def get_stock_info_render(symbol):
    """Render环境获取股票信息的入口函数"""
    if not is_render_environment():
        return None
    return RenderDataProvider.get_stock_info(symbol)


if __name__ == '__main__':
    print(f"Render环境检测: {is_render_environment()}")
    
    # 测试获取K线数据
    df = get_kline_data_render('600519', '20240101', '20241231')
    if df is not None:
        print(f"获取到 {len(df)} 条K线数据")
        print(df.head())
    
    # 测试获取价格
    price = get_current_price_render('600519')
    print(f"当前价格: {price}")
