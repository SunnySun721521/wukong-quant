#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据提供模块 - 提供股票数据获取功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class DataProvider:
    """数据提供类"""
    
    @staticmethod
    def get_kline_data(symbol, start_date, end_date):
        """
        获取股票K线数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        
        Returns:
            DataFrame: 包含K线数据的DataFrame
        """
        try:
            # 首先尝试从 baostock 获取真实数据
            import baostock as bs
            
            # 转换日期格式
            start = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
            
            # 登录 baostock
            lg = bs.login()
            if lg.error_code != '0':
                print(f"baostock登录失败: {lg.error_msg}")
                return DataProvider._get_mock_kline_data(symbol, start_date, end_date)
            
            # 转换股票代码格式
            if symbol.startswith('6'):
                bs_symbol = f"sh.{symbol}"
            elif symbol.startswith('0') or symbol.startswith('3'):
                bs_symbol = f"sz.{symbol}"
            elif symbol.startswith('68'):
                bs_symbol = f"sh.{symbol}"
            else:
                bs_symbol = f"sz.{symbol}"
            
            # 查询历史K线数据
            rs = bs.query_history_k_data_plus(
                bs_symbol,
                "date,open,high,low,close,volume",
                start_date=start,
                end_date=end,
                frequency="d",
                adjustflag="3"  # 复权类型：3表示后复权
            )
            
            if rs.error_code != '0':
                print(f"baostock查询失败: {rs.error_msg}")
                bs.logout()
                return DataProvider._get_mock_kline_data(symbol, start_date, end_date)
            
            # 获取数据
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            bs.logout()
            
            if not data_list:
                print(f"baostock返回空数据，使用模拟数据")
                return DataProvider._get_mock_kline_data(symbol, start_date, end_date)
            
            # 构建DataFrame
            df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 转换数值类型
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 删除缺失值
            df = df.dropna()
            
            print(f"成功从baostock获取 {symbol} 数据: {len(df)} 条记录")
            return df
            
        except Exception as e:
            print(f"从baostock获取数据失败: {e}，使用模拟数据")
            return DataProvider._get_mock_kline_data(symbol, start_date, end_date)
    
    @staticmethod
    def _get_mock_kline_data(symbol, start_date, end_date):
        """生成模拟K线数据（当真实数据源不可用时）"""
        try:
            start = datetime.strptime(start_date, '%Y%m%d')
            end = datetime.strptime(end_date, '%Y%m%d')
            
            # 生成交易日列表（排除周末）
            dates = []
            current = start
            while current <= end:
                if current.weekday() < 5:  # 周一到周五
                    dates.append(current)
                current += timedelta(days=1)
            
            if len(dates) < 30:
                dates = pd.date_range(end - timedelta(days=365), end, freq='B')
            
            # 生成模拟价格数据
            np.random.seed(hash(symbol) % 2**32)
            base_price = random.uniform(10, 100)
            
            prices = [base_price]
            for i in range(1, len(dates)):
                change = random.uniform(-0.03, 0.03)
                new_price = prices[-1] * (1 + change)
                prices.append(new_price)
            
            df = pd.DataFrame({
                'open': [p * (1 + random.uniform(-0.01, 0.01)) for p in prices],
                'high': [p * (1 + random.uniform(0, 0.02)) for p in prices],
                'low': [p * (1 - random.uniform(0, 0.02)) for p in prices],
                'close': prices,
                'volume': [random.randint(1000000, 10000000) for _ in prices]
            }, index=dates)
            
            print(f"使用模拟数据生成 {symbol} 数据: {len(df)} 条记录")
            return df
            
        except Exception as e:
            print(f"生成模拟数据失败: {e}")
            return None
    
    @staticmethod
    def get_current_price(symbol):
        """
        获取股票当前价格
        
        Args:
            symbol: 股票代码
        
        Returns:
            float: 当前价格
        """
        try:
            # 首先尝试从 baostock 获取实时价格
            import baostock as bs
            
            lg = bs.login()
            if lg.error_code != '0':
                print(f"baostock登录失败，返回None")
                return None
            
            # 转换股票代码格式
            if symbol.startswith('6'):
                bs_symbol = f"sh.{symbol}"
            elif symbol.startswith('0') or symbol.startswith('3'):
                bs_symbol = f"sz.{symbol}"
            elif symbol.startswith('68'):
                bs_symbol = f"sh.{symbol}"
            else:
                bs_symbol = f"sz.{symbol}"
            
            # 查询最新价格
            rs = bs.query_history_k_data_plus(
                bs_symbol,
                "close",
                start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d'),
                frequency="d",
                adjustflag="3"
            )
            
            if rs.error_code != '0':
                print(f"baostock查询失败，返回None")
                bs.logout()
                return None
            
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            bs.logout()
            
            if data_list:
                price = float(data_list[-1][0])
                print(f"成功从baostock获取 {symbol} 当前价格: {price}")
                return round(price, 2)
            else:
                print(f"baostock返回空数据，返回None")
                return None
            
        except Exception as e:
            print(f"获取当前价格失败: {e}，返回None")
            return None
    
    @staticmethod
    def _get_mock_current_price(symbol):
        """生成模拟当前价格"""
        np.random.seed(hash(symbol) % 2**32)
        return round(random.uniform(10, 100), 2)
    
    @staticmethod
    def get_stock_info(symbol):
        """
        获取股票信息
        
        Args:
            symbol: 股票代码
        
        Returns:
            dict: 股票信息
        """
        # 股票名称映射
        stock_name_map = {
            "000001": "平安银行",
            "000002": "万科A",
            "000063": "中兴通讯",
            "000100": "TCL科技",
            "000333": "美的集团",
            "000568": "泸州老窖",
            "000651": "格力电器",
            "000725": "京东方A",
            "000723": "美锦能源",
            "000768": "中航西飞",
            "000858": "五粮液",
            "000895": "双汇发展",
            "000977": "浪潮信息",
            "000988": "华工科技",
            "000999": "华润三九",
            "002001": "新和成",
            "002007": "华兰生物",
            "002024": "苏宁易购",
            "002008": "大族激光",
            "002027": "分众传媒",
            "002049": "紫光国微",
            "002120": "韵达股份",
            "002142": "宁波银行",
            "002230": "科大讯飞",
            "002236": "大华股份",
            "002271": "东方雨虹",
            "002304": "洋河股份",
            "002352": "顺丰控股",
            "002368": "太极股份",
            "002371": "北方华创",
            "002415": "海康威视",
            "002460": "赣锋锂业",
            "002475": "立讯精密",
            "002594": "比亚迪",
            "002714": "牧原股份",
            "002747": "埃斯顿",
            "002812": "恩捷股份",
            "003816": "中国广核",
            "300003": "乐普医疗",
            "300014": "亿纬锂能",
            "300015": "爱尔眼科",
            "300024": "机器人",
            "300033": "同花顺",
            "300059": "东方财富",
            "300122": "智飞生物",
            "300124": "汇川技术",
            "300142": "沃森生物",
            "300212": "易华录",
            "300274": "阳光电源",
            "300308": "中际旭创",
            "300402": "宝莱特",
            "300408": "三环集团",
            "300413": "芒果超媒",
            "300433": "蓝思科技",
            "300498": "温氏股份",
            "300502": "新易盛",
            "300750": "宁德时代",
            "300760": "迈瑞医疗",
            "600000": "浦发银行",
            "600009": "上海机场",
            "600016": "民生银行",
            "600028": "中国石化",
            "600030": "中信证券",
            "600031": "三一重工",
            "600036": "招商银行",
            "600048": "保利发展",
            "600050": "中国联通",
            "600104": "上汽集团",
            "600118": "中国卫星",
            "600170": "上海建工",
            "600276": "恒瑞医药",
            "600309": "万华化学",
            "600346": "恒力石化",
            "600406": "国电南瑞",
            "600436": "片仔癀",
            "600438": "通威股份",
            "600519": "贵州茅台",
            "600547": "山东黄金",
            "600570": "恒生电子",
            "600585": "海螺水泥",
            "600588": "用友网络",
            "600600": "青岛啤酒",
            "600660": "福耀玻璃",
            "600690": "海尔智家",
            "600703": "三安光电",
            "600745": "闻泰科技",
            "600760": "中航沈飞",
            "600809": "山西汾酒",
            "600837": "海通证券",
            "600875": "东方电气",
            "600887": "伊利股份",
            "600893": "航发动力",
            "600900": "长江电力",
            "601012": "隆基绿能",
            "601066": "中信建投",
            "601088": "中国神华",
            "601111": "中国国航",
            "601138": "工业富联",
            "601166": "兴业银行",
            "601186": "中国铁建",
            "601288": "农业银行",
            "601318": "中国平安",
            "601319": "中国人保",
            "601328": "交通银行",
            "601336": "新华保险",
            "601390": "中国中铁",
            "601398": "工商银行",
            "601601": "中国太保",
            "601628": "中国人寿",
            "601633": "长城汽车",
            "601668": "中国建筑",
            "601688": "华泰证券",
            "601727": "上海电气",
            "601766": "中国中车",
            "601818": "光大银行",
            "601857": "中国石油",
            "601888": "中国中免",
            "601899": "紫金矿业",
            "601901": "方正证券",
            "601985": "中国核电",
            "601933": "永辉超市",
            "601988": "中国银行",
            "601989": "中国重工",
            "603000": "人民网",
            "603019": "中科曙光",
            "603259": "药明康德",
            "603288": "海天味业",
            "603501": "韦尔股份",
            "603659": "璞泰来",
            "603799": "华友钴业",
            "603986": "兆易创新",
            "603993": "洛阳钼业",
            "688008": "澜起科技",
            "688009": "中国通号",
            "688012": "中微公司",
            "688036": "传音控股",
            "688111": "金山办公",
            "688126": "沪硅产业",
            "688169": "石头科技",
            "688185": "康希诺",
            "688339": "亿华通",
            "688599": "天合光能",
            "688981": "中芯国际",
            "301269": "恒而达"
        }
        
        return {
            'symbol': symbol,
            'name': stock_name_map.get(symbol, f'股票{symbol}')
        }
