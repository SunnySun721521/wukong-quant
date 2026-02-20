#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票池管理模块 - 管理股票池和沪深300成分股
"""

import os
import json

class StockPoolManager:
    """股票池管理类"""
    
    # 默认股票池
    DEFAULT_POOL = [
        "000001", "000002", "000063", "000100", "000333",
        "000568", "000651", "000725", "000768", "000858",
        "000895", "002001", "002007", "002027", "002049",
        "002120", "002142", "002230", "002236", "002271",
        "002304", "002352", "002415", "002460", "002475",
        "002594", "002714", "002812", "003816", "300003",
        "300014", "300015", "300033", "300059", "300122",
        "300124", "300142", "300274", "300408", "300413",
        "300433", "300498", "300750", "300760", "600000",
        "600009", "600016", "600028", "600030", "600031",
        "600036", "600048", "600050", "600104", "600276",
        "600309", "600346", "600406", "600436", "600438",
        "600519", "600547", "600570", "600585", "600588",
        "600600", "600660", "600690", "600703", "600745",
        "600809", "600837", "600887", "600893", "600900",
        "601012", "601066", "601088", "601111", "601138",
        "601166", "601186", "601288", "601318", "601319",
        "601328", "601336", "601390", "601398", "601601",
        "601628", "601633", "601668", "601688", "601727",
        "601766", "601818", "601857", "601888", "601899",
        "601901", "601933", "601988", "601989", "603288",
        "603501", "603659", "603799", "603986", "603993",
        "688008", "688009", "688012", "688036", "688111",
        "688126", "688169", "688185", "688599", "688981"
    ]
    
    # 沪深300成分股（简化版，使用前100只）
    HS300_COMPONENTS = DEFAULT_POOL[:100]
    
    def __init__(self, log_dir=None):
        self.log_dir = log_dir
        self.pool_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'strategy', 'data', 'stock_pool.json')
        self.current_pool = self._load_pool()
        self.hs300_components = self.HS300_COMPONENTS.copy()
    
    def _load_pool(self):
        """从文件加载股票池数据"""
        try:
            if os.path.exists(self.pool_file):
                with open(self.pool_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data and isinstance(data, list):
                        print(f"从文件加载股票池: {len(data)}只股票")
                        return data
                    elif data and isinstance(data, dict) and 'stocks' in data:
                        stocks = data.get('stocks', [])
                        if stocks and isinstance(stocks, list):
                            print(f"从文件加载股票池: {len(stocks)}只股票")
                            return stocks
        except Exception as e:
            print(f"加载股票池文件失败: {e}")
        
        print(f"使用默认股票池: {len(self.DEFAULT_POOL)}只股票")
        return self.DEFAULT_POOL.copy()
    
    def _save_pool(self):
        """将股票池数据保存到文件"""
        try:
            os.makedirs(os.path.dirname(self.pool_file), exist_ok=True)
            with open(self.pool_file, 'w', encoding='utf-8') as f:
                json.dump({"stocks": self.current_pool, "last_updated": str(__import__('datetime').datetime.now())}, f, ensure_ascii=False, indent=2)
            print(f"股票池已保存到文件: {len(self.current_pool)}只股票")
        except Exception as e:
            print(f"保存股票池文件失败: {e}")
    
    def get_pool(self):
        """获取当前股票池"""
        return self.current_pool
    
    def get_stock_pool_info(self):
        """获取股票池详细信息（API兼容方法）"""
        return {
            'current_pool': self.current_pool,
            'default_pool': self.DEFAULT_POOL,
            'pool_size': len(self.current_pool),
            'hs300_components': self.hs300_components,
            'hs300_size': len(self.hs300_components)
        }
    
    def set_pool(self, symbols):
        """设置股票池"""
        self.current_pool = symbols
        self._save_pool()
    
    def set_custom_pool(self, stocks):
        """设置自定义股票池（API兼容方法）"""
        self.current_pool = stocks
        self._save_pool()
    
    def add_stock(self, symbol):
        """添加股票到池"""
        if symbol not in self.current_pool:
            self.current_pool.append(symbol)
            self._save_pool()
    
    def add_custom_stock(self, stock):
        """添加股票到池（API兼容方法）"""
        if stock not in self.current_pool:
            self.current_pool.append(stock)
            self._save_pool()
            return True
        return False
    
    def remove_stock(self, symbol):
        """从池中移除股票"""
        if symbol in self.current_pool:
            self.current_pool.remove(symbol)
            self._save_pool()
    
    def remove_custom_stock(self, stock):
        """从池中移除股票（API兼容方法）"""
        if stock in self.current_pool:
            self.current_pool.remove(stock)
            self._save_pool()
            return True
        return False
    
    def reset_to_default(self):
        """重置为默认股票池"""
        self.current_pool = self.DEFAULT_POOL.copy()
        self._save_pool()
    
    def get_hs300_components(self):
        """获取沪深300成分股"""
        return self.hs300_components
