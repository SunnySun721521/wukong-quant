#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render数据获取模块 - 优先使用本地缓存数据
不影响本地程序运行
"""

import os

def patch_data_providers():
    """修补数据提供器，在 Render 环境中优先使用本地数据"""
    import os
    if not (os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_NAME')):
        return False
    
    print("[Render] 修补数据提供器...")
    
    try:
        from strategy import data_provider
        
        original_get_kline = data_provider.DataProvider.get_kline_data
        
        def patched_get_kline(symbol, start_date, end_date):
            """修补后的获取K线数据 - 优先使用本地数据"""
            print(f"[Render] 获取K线数据: {symbol}")
            
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'strategy', 'data'
            )
            
            cache_file = os.path.join(data_dir, f'kline_{symbol}.csv')
            if os.path.exists(cache_file):
                print(f"[Render] 使用本地K线缓存: {cache_file}")
                import pandas as pd
                try:
                    df = pd.read_csv(cache_file)
                    if not df.empty:
                        return df
                except Exception as e:
                    print(f"[Render] 读取缓存失败: {e}")
            
            try:
                return original_get_kline(symbol, start_date, end_date)
            except Exception as e:
                print(f"[Render] 获取数据失败，回退到模拟数据: {e}")
                return data_provider.DataProvider._get_mock_kline_data(symbol, start_date, end_date)
        
        data_provider.DataProvider.get_kline_data = staticmethod(patched_get_kline)
        print("[Render] 数据提供器修补完成")
        return True
        
    except Exception as e:
        print(f"[Render] 修补数据提供器失败: {e}")
        return False

def download_render_data():
    """在Render环境中下载数据"""
    import os
    if not (os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_NAME')):
        return
    
    print("[Render] 开始下载数据...")
    
    try:
        import baostock as bs
        
        lg = bs.login()
        if lg.error_code != '0':
            print(f"[Render] baostock 登录失败，跳过数据下载")
            return
        
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'strategy', 'data'
        )
        os.makedirs(data_dir, exist_ok=True)
        
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        print(f"[Render] 下载沪深300数据: {start_date} - {end_date}")
        
        rs = bs.query_history_k_data_plus(
            "sh.000300",
            "date,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="3"
        )
        
        if rs.error_code == '0':
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if data_list:
                import pandas as pd
                df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                hs300_file = os.path.join(data_dir, 'hs300_data.csv')
                df.to_csv(hs300_file, index=False)
                print(f"[Render] 沪深300数据已保存: {len(df)} 条")
        
        bs.logout()
        print("[Render] 数据下载完成")
        
    except Exception as e:
        print(f"[Render] 数据下载失败: {e}")
