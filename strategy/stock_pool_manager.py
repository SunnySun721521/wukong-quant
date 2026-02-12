#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
from .data_provider import DataProvider

try:
    import adata
    ADATA_AVAILABLE = True
except ImportError:
    ADATA_AVAILABLE = False

try:
    import akshare as ak
    AK_SHARE_AVAILABLE = True
except ImportError:
    AK_SHARE_AVAILABLE = False

class StockPoolManager:
    def __init__(self, initial_stocks=None, log_dir="./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        self.stock_pool_file = os.path.join(log_dir, "stock_pool.json")
        self.hs300_file = os.path.join(log_dir, "hs300_components.json")
        
        self.initial_stocks = initial_stocks or ['600519', '002371', '000858', '002415', '002236']
        self.current_pool = self.load_stock_pool()
        self.hs300_components = self.load_hs300_components()
    
    def load_stock_pool(self):
        if os.path.exists(self.stock_pool_file):
            with open(self.stock_pool_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('stocks', self.initial_stocks)
        return self.initial_stocks.copy()
    
    def save_stock_pool(self, pool=None):
        pool = pool or self.current_pool
        with open(self.stock_pool_file, 'w', encoding='utf-8') as f:
            json.dump({
                'stocks': pool,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }, f, ensure_ascii=False, indent=2)
    
    def load_hs300_components(self):
        if os.path.exists(self.hs300_file):
            with open(self.hs300_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                last_update = datetime.strptime(data.get('last_updated', '2020-01-01'), '%Y-%m-%d %H:%M:%S')
                if (datetime.now() - last_update).days < 7:
                    return data.get('stocks', [])
        
        return self.fetch_hs300_components()
    
    def fetch_hs300_components(self):
        try:
            components = DataProvider.get_hs300_components()
            
            if components:
                with open(self.hs300_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'stocks': components,
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }, f, ensure_ascii=False, indent=2)
                
                return components
        except Exception as e:
            print(f"获取沪深300成分股失败: {e}")
        
        return []
    
    def update_hs300_components(self):
        self.hs300_components = self.fetch_hs300_components()
        return self.hs300_components
    
    def adjust_stock_pool(self, custom_stocks=None):
        custom_stocks = custom_stocks or self.current_pool
        
        if not self.hs300_components:
            self.update_hs300_components()
        
        removed = []
        for stock in custom_stocks:
            if stock not in self.hs300_components:
                removed.append(stock)
        
        adjusted_pool = [s for s in custom_stocks if s not in removed]
        
        return adjusted_pool, removed
    
    def select_new_stocks(self, num_stocks=1, exclude_stocks=None):
        exclude_stocks = exclude_stocks or []
        
        if not self.hs300_components:
            self.update_hs300_components()
        
        available_stocks = [s for s in self.hs300_components if s not in exclude_stocks and s not in self.current_pool]
        
        if not available_stocks:
            return []
        
        # 方法1: 使用adata获取实时行情（第一选择）
        if ADATA_AVAILABLE:
            try:
                df = adata.stock.market.get_market()
                if df is not None and not df.empty:
                    available_data = df[df['stock_code'].isin(available_stocks)]
                    if not available_data.empty:
                        # 按市值排序（adata没有总市值，使用成交量作为替代）
                        available_data = available_data.sort_values(by=['volume'], ascending=False)
                        new_stocks = available_data['stock_code'].head(num_stocks).tolist()
                        return new_stocks
            except Exception as e:
                print(f"adata选股失败: {e}")
        
        # 方法2: 使用akshare获取实时行情（备选）
        if AK_SHARE_AVAILABLE:
            try:
                stock_data = ak.stock_zh_a_spot_em()
                available_data = stock_data[stock_data['代码'].isin(available_stocks)]
                
                if not available_data.empty:
                    available_data = available_data.sort_values(by=['总市值'], ascending=False)
                    new_stocks = available_data['代码'].head(num_stocks).tolist()
                    return new_stocks
            except Exception as e:
                print(f"akshare选股失败: {e}")
        
        return available_stocks[:num_stocks]
    
    def get_default_pool(self):
        """获取默认股票池"""
        return self.initial_stocks.copy()
    
    def get_stock_pool_info(self):
        # 获取每个股票的详细信息，包括名称
        stock_details = []
        try:
            for symbol in self.current_pool:
                try:
                    # 直接使用默认名称，避免API调用失败
                    stock_details.append({
                        'symbol': symbol,
                        'name': self.get_stock_name(symbol)
                    })
                except Exception as e:
                    print(f"获取股票 {symbol} 信息失败: {e}")
                    stock_details.append({
                        'symbol': symbol,
                        'name': f'股票{symbol}'
                    })
        except Exception as e:
            print(f"构建股票详细信息失败: {e}")
            stock_details = []
            for symbol in self.current_pool:
                stock_details.append({
                    'symbol': symbol,
                    'name': f'股票{symbol}'
                })
        
        return {
            'current_pool': self.current_pool,
            'stock_details': stock_details,
            'pool_size': len(self.current_pool),
            'hs300_size': len(self.hs300_components),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_stock_name(self, symbol):
        # 股票名称映射
        stock_names = {
            # 银行股
            '000001': '平安银行',
            '600036': '招商银行',
            '601398': '工商银行',
            '601288': '农业银行',
            '601988': '中国银行',
            '600016': '民生银行',
            '601166': '兴业银行',
            '600000': '浦发银行',
            '601818': '光大银行',
            '600926': '杭州银行',
            '601128': '常熟银行',
            
            # 保险股
            '601318': '中国平安',
            '601628': '中国人寿',
            '601336': '新华保险',
            '601601': '中国太保',
            
            # 券商股
            '600030': '中信证券',
            '601688': '华泰证券',
            '601211': '国泰君安',
            '600837': '海通证券',
            '601901': '方正证券',
            '601066': '中信建投',
            '600999': '招商证券',
            '601788': '光大证券',
            '600109': '国金证券',
            '600369': '西南证券',
            
            # 白酒股
            '600519': '贵州茅台',
            '000858': '五粮液',
            '000568': '泸州老窖',
            '600809': '山西汾酒',
            '000799': '酒鬼酒',
            '600702': '舍得酒业',
            '002304': '洋河股份',
            '600559': '老白干酒',
            
            # 科技股
            '000063': '中兴通讯',
            '000977': '浪潮信息',
            '600410': '华胜天成',
            '300496': '中科创达',
            '300750': '宁德时代',
            '002415': '海康威视',
            '002371': '北方华创',
            '000938': '紫光股份',
            '600588': '用友网络',
            '300207': '欣旺达',
            '300136': '信维通信',
            '002185': '华天科技',
            '300308': '中际旭创',
            '300502': '新易盛',
            '300274': '阳光电源',
            '002594': '比亚迪',
            '300014': '亿纬锂能',
            '002460': '赣锋锂业',
            '002340': '格林美',
            '601012': '隆基绿能',
            
            # 医药股
            '600276': '恒瑞医药',
            '601607': '上海医药',
            '000999': '华润三九',
            '300003': '乐普医疗',
            '600196': '复星医药',
            '600521': '华海药业',
            '002223': '鱼跃医疗',
            '300347': '泰格医药',
            '600867': '通化东宝',
            
            # 消费股
            '600887': '伊利股份',
            '000333': '美的集团',
            '000651': '格力电器',
            '601888': '中国中免',
            '002027': '分众传媒',
            '600690': '海尔智家',
            '601111': '中国国航',
            '600029': '南方航空',
            
            # 其他股票
            '603000': '人民网',
            '600170': '上海建工',
            '300024': '机器人',
            '600518': '康美药业',
            '600031': '三一重工',
            '601899': '紫金矿业',
            '601668': '中国建筑',
            '600028': '中国石化',
            '601857': '中国石油',
            '601669': '中国电建',
            '601800': '中国交建',
            '601186': '中国铁建',
            '601390': '中国中铁',
            '600019': '宝钢股份',
            '601006': '大秦铁路',
            '000002': '万科A',
            '301269': '华大九天',
            # 热门股票
            '688981': '中芯国际',
            '688599': '天合光能',
            '688396': '华润微',
            '601766': '中国中车',
            '600157': '永泰能源',
            '688256': '寒武纪',
            '300563': '神宇股份',
            '002079': '苏州固锝',
            # 其他股票
            '601985': '中国核电',
            '000988': '华工科技',
            '002008': '大族激光',
            '300124': '汇川技术',
            '300760': '迈瑞医疗',
            # 缺失股票补充
            '601727': '上海电气',
            '600875': '东方电气',
            '603019': '中科曙光',
            '601138': '工业富联',
            '688012': '中微公司',
            '300212': '易华录',
            '002368': '太极股份',
            '600406': '国电南瑞',
            '003816': '中国广核',
            '300402': '宝色股份',
            '688339': '亿华通',
            '000723': '美锦能源',
            '002747': '埃斯顿',
            '600893': '航发动力',
            '600118': '中国卫星',
            '600760': '中航沈飞',
            '000768': '中航西飞',
            '603259': '药明康德'
        }
        return stock_names.get(symbol, f'股票{symbol}')
    
    def add_custom_stock(self, stock_code):
        if stock_code not in self.current_pool:
            self.current_pool.append(stock_code)
            self.save_stock_pool()
            return True
        return False
    
    def remove_custom_stock(self, stock_code):
        if stock_code in self.current_pool:
            self.current_pool.remove(stock_code)
            self.save_stock_pool()
            return True
        return False
    
    def set_custom_pool(self, stock_list):
        self.current_pool = stock_list.copy()
        self.save_stock_pool()
        return True