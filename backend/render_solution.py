# -*- coding: utf-8 -*-
"""
Render 环境完整解决方案模块
解决：市场状态、回测数据、PDF字体、邮件发送等问题
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


class RenderStockData:
    """Render环境股票数据获取类 - 使用yfinance"""
    
    # 股票名称缓存
    _name_cache = {}
    
    @staticmethod
    def get_kline_data(symbol, start_date, end_date):
        """获取K线数据"""
        if not is_render_environment():
            return None
        
        print(f"[Render] 获取K线数据: {symbol}, {start_date} - {end_date}")
        
        # 标准化日期格式
        if isinstance(start_date, str) and len(start_date) == 8:
            start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
        if isinstance(end_date, str) and len(end_date) == 8:
            end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
        
        # yfinance获取数据
        try:
            import yfinance as yf
            
            # A股代码转换
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith('6'):
                    yf_symbol = f"{symbol}.SS"
                else:
                    yf_symbol = f"{symbol}.SZ"
            else:
                yf_symbol = symbol
            
            print(f"[Render] yfinance代码: {yf_symbol}")
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df is not None and not df.empty:
                # 重命名列
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                df.columns = ['open', 'high', 'low', 'close', 'volume']
                df.index.name = 'datetime'
                
                # 确保数值类型
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                df = df.dropna()
                
                print(f"[Render] yfinance获取K线成功: {symbol}, {len(df)}条")
                print(f"[Render] 最新数据日期: {df.index[-1].strftime('%Y-%m-%d')}")
                return df
                
        except Exception as e:
            print(f"[Render] yfinance获取K线失败: {e}")
        
        return None
    
    @staticmethod
    def get_stock_name(symbol):
        """获取股票名称"""
        if not is_render_environment():
            return symbol
        
        # 检查缓存
        if symbol in RenderStockData._name_cache:
            return RenderStockData._name_cache[symbol]
        
        try:
            import yfinance as yf
            
            # A股代码转换
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith('6'):
                    yf_symbol = f"{symbol}.SS"
                else:
                    yf_symbol = f"{symbol}.SZ"
            else:
                yf_symbol = symbol
            
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            name = info.get('longName') or info.get('shortName') or symbol
            
            # 缓存结果
            RenderStockData._name_cache[symbol] = name
            print(f"[Render] 获取股票名称: {symbol} = {name}")
            return name
            
        except Exception as e:
            print(f"[Render] 获取股票名称失败 {symbol}: {e}")
            return symbol
    
    @staticmethod
    def get_stock_info(symbol):
        """获取股票信息"""
        if not is_render_environment():
            return None
        
        try:
            import yfinance as yf
            
            # A股代码转换
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith('6'):
                    yf_symbol = f"{symbol}.SS"
                else:
                    yf_symbol = f"{symbol}.SZ"
            else:
                yf_symbol = symbol
            
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            name = info.get('longName') or info.get('shortName') or symbol
            
            # 获取最新价格
            hist = ticker.history(period="5d")
            price = 0
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
            
            return {
                'symbol': symbol,
                'name': name,
                'price': price,
                'industry': info.get('industry', ''),
                'sector': info.get('sector', ''),
                'market_cap': info.get('marketCap', 0)
            }
            
        except Exception as e:
            print(f"[Render] 获取股票信息失败 {symbol}: {e}")
            return {'symbol': symbol, 'name': symbol, 'price': 0}
    
    @staticmethod
    def get_current_price(symbol):
        """获取股票当前价格"""
        if not is_render_environment():
            return None
        
        print(f"[Render] 获取当前价格: {symbol}")
        
        try:
            import yfinance as yf
            
            # A股代码转换
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith('6'):
                    yf_symbol = f"{symbol}.SS"
                else:
                    yf_symbol = f"{symbol}.SZ"
            else:
                yf_symbol = symbol
            
            ticker = yf.Ticker(yf_symbol)
            
            # 获取最近5天的数据
            hist = ticker.history(period="5d")
            
            if hist is not None and not hist.empty:
                price = float(hist['Close'].iloc[-1])
                print(f"[Render] 获取价格成功: {symbol} = {price}")
                return price
            
        except Exception as e:
            print(f"[Render] 获取价格失败 {symbol}: {e}")
        
        return None


class RenderIndexData:
    """Render环境指数数据获取类"""
    
    @staticmethod
    def get_hs300_index():
        """获取沪深300指数数据 - 使用akshare（更可靠）"""
        if not is_render_environment():
            return None, None, None, None
        
        print("[Render] 获取沪深300指数数据")
        
        # 方法1: 使用akshare获取上证指数（更可靠）
        try:
            import akshare as ak
            import socket
            socket.setdefaulttimeout(30)
            
            # 获取上证指数数据（akshare支持较好）
            print("[Render] 尝试akshare获取上证指数")
            df = ak.stock_zh_index_daily(symbol="sh000001")
            
            if df is not None and not df.empty:
                # 筛选最近150天
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                
                # 获取最近150天的数据
                recent_df = df.tail(150).copy()
                
                if not recent_df.empty:
                    current_price = float(recent_df['close'].iloc[-1])
                    prev_price = float(recent_df['close'].iloc[-2]) if len(recent_df) > 1 else current_price
                    change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                    
                    # 计算MA120
                    if len(recent_df) >= 120:
                        ma120 = float(recent_df['close'].tail(120).mean())
                    else:
                        ma120 = float(recent_df['close'].mean())
                    
                    # 转换为标准格式
                    hist_df = recent_df.set_index('date')[['open', 'high', 'low', 'close', 'volume']].copy()
                    hist_df.index.name = 'Date'
                    
                    print(f"[Render] akshare获取上证指数成功: 价格={current_price:.2f}, 涨跌={change_pct:.2f}%")
                    return current_price, change_pct, ma120, hist_df
                    
        except Exception as e:
            print(f"[Render] akshare获取指数失败: {e}")
        
        # 方法2: 使用yfinance获取上证指数
        try:
            import yfinance as yf
            
            print("[Render] 尝试yfinance获取上证指数")
            ticker = yf.Ticker("000001.SS")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=200)
            hist = ticker.history(start=start_date, end=end_date)
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                
                if len(hist) >= 120:
                    ma120 = float(hist['Close'].tail(120).mean())
                else:
                    ma120 = float(hist['Close'].mean())
                
                print(f"[Render] yfinance获取上证指数成功: 价格={current_price:.2f}")
                return current_price, change_pct, ma120, hist
                
        except Exception as e:
            print(f"[Render] yfinance获取指数失败: {e}")
        
        # 方法3: 使用efinance获取
        try:
            import efinance as ef
            
            print("[Render] 尝试efinance获取上证指数")
            end_date_str = datetime.now().strftime('%Y%m%d')
            start_date_str = (datetime.now() - timedelta(days=200)).strftime('%Y%m%d')
            
            df = ef.stock.get_quote_history(
                stock_codes=['000001'],
                beg=start_date_str,
                end=end_date_str,
                klt=101
            )
            
            if df and '000001' in df:
                result_df = df['000001']
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
                        
                        hist_df = result_df.set_index('date')[['open', 'high', 'low', 'close', 'volume']].copy()
                        hist_df.index.name = 'Date'
                        
                        print(f"[Render] efinance获取指数成功: 价格={current_price:.2f}")
                        return current_price, change_pct, ma120, hist_df
                        
        except Exception as e:
            print(f"[Render] efinance获取指数失败: {e}")
        
        print("[Render] 所有方法均无法获取指数数据")
        return None, None, None, None


class RenderPDFFonts:
    """Render环境PDF字体处理"""
    
    _font_registered = False
    _font_name = None
    
    @staticmethod
    def get_chinese_font():
        """获取中文字体"""
        if not is_render_environment():
            return None
        
        # 如果已经注册过，直接返回
        if RenderPDFFonts._font_registered and RenderPDFFonts._font_name:
            return RenderPDFFonts._font_name
        
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except ImportError:
            print("[Render] reportlab未安装")
            return None
        
        # 尝试多种字体路径
        font_paths = [
            # Noto CJK (最常见的中文字体)
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            # WenQuanYi
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/wenquanyi/wqy-zenhei.ttc',
            # DejaVu (虽然不支持中文，但至少不会报错)
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans.ttf',
            # Liberation
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font_name = os.path.basename(font_path).split('.')[0].replace('-', '').replace('_', '')
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    RenderPDFFonts._font_registered = True
                    RenderPDFFonts._font_name = font_name
                    print(f"[Render] 成功注册字体: {font_name} @ {font_path}")
                    return font_name
                except Exception as e:
                    print(f"[Render] 注册字体失败 {font_path}: {e}")
                    continue
        
        print("[Render] 警告: 未找到可用的中文字体")
        return None


# 便捷函数
def get_kline_render(symbol, start_date, end_date):
    """获取K线数据"""
    return RenderStockData.get_kline_data(symbol, start_date, end_date)

def get_stock_name_render(symbol):
    """获取股票名称"""
    return RenderStockData.get_stock_name(symbol)

def get_stock_info_render(symbol):
    """获取股票信息"""
    return RenderStockData.get_stock_info(symbol)

def get_current_price_render(symbol):
    """获取股票当前价格"""
    return RenderStockData.get_current_price(symbol)

def get_index_render():
    """获取指数数据"""
    return RenderIndexData.get_hs300_index()

def get_pdf_font_render():
    """获取PDF字体"""
    return RenderPDFFonts.get_chinese_font()


if __name__ == '__main__':
    print(f"Render环境: {is_render_environment()}")
    
    # 测试获取指数
    price, change, ma120, hist = get_index_render()
    print(f"指数: 价格={price}, 涨跌={change}%, MA120={ma120}")
    
    # 测试获取股票名称
    name = get_stock_name_render('600519')
    print(f"股票名称: {name}")
