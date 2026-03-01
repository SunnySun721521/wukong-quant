# -*- coding: utf-8 -*-
"""
Render 环境数据获取模块
在 Render 环境下优先使用 yfinance 获取数据
不影响本地程序的正常运行
"""
import os
import sys
from datetime import datetime, timedelta

RENDER_ENV = os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_ID')

def is_render_environment():
    """检测是否在 Render 环境"""
    return RENDER_ENV is not None

def get_a_stock_price_render(symbol):
    """在 Render 环境获取 A 股价格 - 优先使用 yfinance"""
    if not is_render_environment():
        return None
    
    # 方法1: yfinance (Render 环境首选)
    try:
        import yfinance as yf
        if symbol.startswith('6'):
            yf_symbol = f"{symbol}.SS"
        else:
            yf_symbol = f"{symbol}.SZ"
        
        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(period="5d")
        if not hist.empty:
            price = float(hist['Close'].iloc[-1])
            print(f"yfinance获取到 {symbol} 价格: {price}")
            return price
    except Exception as e:
        print(f"yfinance获取失败: {e}")
    
    # 方法2: efinance
    try:
        import efinance as ef
        df = ef.stock.get_realtime_quotes()
        if df is not None and not df.empty:
            df.columns = df.columns.str.replace(' ', '')
            stock_df = df[df['股票代码'] == symbol]
            if not stock_df.empty:
                price = float(stock_df['最新价'].values[0])
                print(f"efinance获取到 {symbol} 价格: {price}")
                return price
    except Exception as e:
        print(f"efinance获取失败: {e}")
    
    # 方法3: akshare
    try:
        import akshare as ak
        import socket
        socket.setdefaulttimeout(30)
        df = ak.stock_zh_a_spot_em()
        if df is not None and not df.empty:
            stock_df = df[df['代码'] == symbol]
            if not stock_df.empty:
                price = float(stock_df['最新价'].values[0])
                print(f"akshare获取到 {symbol} 价格: {price}")
                return price
    except Exception as e:
        print(f"akshare获取失败: {e}")
    
    # 方法4: baostock
    try:
        import baostock as bs
        lg = bs.login()
        if lg.error_code == '0':
            if symbol.startswith('6'):
                bs_code = f"sh.{symbol}"
            else:
                bs_code = f"sz.{symbol}"
            
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,close",
                start_date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                end_date=datetime.now().strftime("%Y-%m-%d"),
                frequency="d"
            )
            if rs.error_code == '0':
                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())
                if data_list and len(data_list) > 0:
                    price = float(data_list[-1][1])
                    print(f"baostock获取到 {symbol} 价格: {price}")
                    bs.logout()
                    return price
            bs.logout()
    except Exception as e:
        print(f"baostock获取失败: {e}")
    
    return None


def get_hs300_index_render():
    """在 Render 环境获取沪深300指数"""
    if not is_render_environment():
        return None, None
    
    try:
        import yfinance as yf
        ticker = yf.Ticker("000300.SS")
        hist = ticker.history(period="5d")
        if not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
            prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
            print(f"yfinance获取沪深300: {current_price}, 涨跌幅: {change_pct}%")
            return current_price, change_pct
    except Exception as e:
        print(f"yfinance获取沪深300失败: {e}")
    
    return None, None


def get_stock_price_with_fallback(symbol):
    """获取股票价格，Render 环境优先 yfinance，本地保持原有逻辑"""
    if is_render_environment():
        price = get_a_stock_price_render(symbol)
        if price:
            return price
    
    return None


if __name__ == '__main__':
    print(f"Render 环境: {is_render_environment()}")
    price = get_a_stock_price_render('600519')
    print(f"600519 价格: {price}")
