# -*- coding: utf-8 -*-
"""
统一数据库管理器 - 用于存储所有缓存数据
该数据库可以被Git版本控制，确保数据在不同部署环境间同步
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

class UnifiedDatabase:
    """统一数据库类"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'data', 'wukong_data.db')
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. 回测股票池表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backtest_pool (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL UNIQUE,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 2. 持仓数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    name TEXT,
                    shares INTEGER,
                    cost_price REAL,
                    current_price REAL,
                    change_pct REAL,
                    market_value REAL,
                    profit_loss REAL,
                    profit_pct REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 3. 股票池表（选股池）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_pool (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 4. 邮箱配置表（加密存储）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT NOT NULL UNIQUE,
                    config_value TEXT,
                    config_type TEXT DEFAULT 'string',
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 5. 邮箱收件人表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_address TEXT NOT NULL UNIQUE,
                    is_active INTEGER DEFAULT 1,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 6. 价格缓存表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL UNIQUE,
                    price REAL,
                    change_pct REAL,
                    volume REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 7. 现金配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cash_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT NOT NULL UNIQUE,
                    config_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 8. 回测结果缓存表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backtest_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    strategy_type TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    win_rate REAL,
                    total_trades INTEGER,
                    total_return REAL,
                    max_drawdown REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            print(f"统一数据库初始化完成: {self.db_path}")
    
    # ========== 回测股票池操作 ==========
    def get_backtest_pool(self) -> List[str]:
        """获取回测股票池"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT stock_code FROM backtest_pool ORDER BY added_at")
            return [row[0] for row in cursor.fetchall()]
    
    def save_backtest_pool(self, stocks: List[str]) -> bool:
        """保存回测股票池"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM backtest_pool")
                for stock in stocks:
                    cursor.execute("INSERT INTO backtest_pool (stock_code) VALUES (?)", (stock,))
                conn.commit()
            return True
        except Exception as e:
            print(f"保存回测股票池失败: {e}")
            return False
    
    # ========== 持仓数据操作 ==========
    def get_positions(self) -> List[Dict]:
        """获取持仓数据"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM positions ORDER BY symbol")
            return [dict(row) for row in cursor.fetchall()]
    
    def save_positions(self, positions: List[Dict]) -> bool:
        """保存持仓数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM positions")
                for pos in positions:
                    cursor.execute('''
                        INSERT INTO positions (symbol, name, shares, cost_price, current_price, 
                                             change_pct, market_value, profit_loss, profit_pct, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (pos.get('symbol'), pos.get('name'), pos.get('shares'), 
                          pos.get('cost_price'), pos.get('current_price'),
                          pos.get('change_pct'), pos.get('market_value'),
                          pos.get('profit_loss'), pos.get('profit_pct'),
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
            return True
        except Exception as e:
            print(f"保存持仓数据失败: {e}")
            return False
    
    # ========== 股票池操作 ==========
    def get_stock_pool(self) -> List[Dict]:
        """获取股票池"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stock_pool ORDER BY added_at")
            return [dict(row) for row in cursor.fetchall()]
    
    def save_stock_pool(self, stocks: List[Dict]) -> bool:
        """保存股票池"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM stock_pool")
                for stock in stocks:
                    cursor.execute('''
                        INSERT INTO stock_pool (stock_code, stock_name, added_at)
                        VALUES (?, ?, ?)
                    ''', (stock.get('code'), stock.get('name'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
            return True
        except Exception as e:
            print(f"保存股票池失败: {e}")
            return False
    
    # ========== 邮箱配置操作 ==========
    def get_email_config(self) -> Dict:
        """获取邮箱配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT config_key, config_value, config_type FROM email_config")
            config = {}
            for row in cursor.fetchall():
                key, value, config_type = row
                if config_type == 'boolean':
                    config[key] = value.lower() == 'true' if value else False
                elif config_type == 'integer':
                    config[key] = int(value) if value else 0
                elif config_type == 'json':
                    config[key] = json.loads(value) if value else []
                else:
                    config[key] = value
            return config
    
    def save_email_config(self, config: Dict) -> bool:
        """保存邮箱配置"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for key, value in config.items():
                    if isinstance(value, bool):
                        config_type = 'boolean'
                        value_str = 'true' if value else 'false'
                    elif isinstance(value, int):
                        config_type = 'integer'
                        value_str = str(value)
                    elif isinstance(value, (list, dict)):
                        config_type = 'json'
                        value_str = json.dumps(value, ensure_ascii=False)
                    else:
                        config_type = 'string'
                        value_str = str(value) if value else ''
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO email_config (config_key, config_value, config_type, updated_at)
                        VALUES (?, ?, ?, ?)
                    ''', (key, value_str, config_type, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
            return True
        except Exception as e:
            print(f"保存邮箱配置失败: {e}")
            return False
    
    def get_email_recipients(self) -> List[str]:
        """获取邮箱收件人"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email_address FROM email_recipients WHERE is_active = 1")
            return [row[0] for row in cursor.fetchall()]
    
    def save_email_recipients(self, recipients: List[str]) -> bool:
        """保存邮箱收件人"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM email_recipients")
                for email in recipients:
                    cursor.execute("INSERT INTO email_recipients (email_address) VALUES (?)", (email,))
                conn.commit()
            return True
        except Exception as e:
            print(f"保存邮箱收件人失败: {e}")
            return False
    
    # ========== 价格缓存操作 ==========
    def get_price_cache(self) -> Dict:
        """获取价格缓存"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol, price, change_pct, volume, timestamp FROM price_cache")
            cache = {}
            for row in cursor.fetchall():
                cache[row[0]] = {
                    'price': row[1],
                    'change_pct': row[2],
                    'volume': row[3],
                    'timestamp': row[4]
                }
            return cache
    
    def save_price_cache(self, cache: Dict) -> bool:
        """保存价格缓存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM price_cache")
                for symbol, data in cache.items():
                    cursor.execute('''
                        INSERT INTO price_cache (symbol, price, change_pct, volume, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (symbol, data.get('price'), data.get('change_pct'), 
                          data.get('volume'), data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))))
                conn.commit()
            return True
        except Exception as e:
            print(f"保存价格缓存失败: {e}")
            return False
    
    # ========== 现金配置操作 ==========
    def get_cash_config(self) -> Dict:
        """获取现金配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT config_key, config_value FROM cash_config")
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    def save_cash_config(self, config: Dict) -> bool:
        """保存现金配置"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for key, value in config.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO cash_config (config_key, config_value, updated_at)
                        VALUES (?, ?, ?)
                    ''', (key, str(value), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
            return True
        except Exception as e:
            print(f"保存现金配置失败: {e}")
            return False


# 单例实例
_unified_db = None

def get_unified_db() -> UnifiedDatabase:
    """获取统一数据库单例"""
    global _unified_db
    if _unified_db is None:
        _unified_db = UnifiedDatabase()
    return _unified_db


def migrate_all_data():
    """迁移所有现有数据到统一数据库"""
    print("=== 开始数据迁移 ===")
    
    db = get_unified_db()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. 迁移回测股票池
    try:
        backtest_pool_file = os.path.join(base_dir, 'strategy', 'data', 'backtest_pool.json')
        if os.path.exists(backtest_pool_file):
            with open(backtest_pool_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stocks = data.get('stocks', [])
                db.save_backtest_pool(stocks)
                print(f"迁移回测股票池: {len(stocks)} 只股票")
    except Exception as e:
        print(f"迁移回测股票池失败: {e}")
    
    # 2. 迁移持仓数据
    try:
        position_file = os.path.join(base_dir, 'strategy', 'data', 'position_data.csv')
        if os.path.exists(position_file):
            import csv
            positions = []
            with open(position_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                positions = list(reader)
            db.save_positions(positions)
            print(f"迁移持仓数据: {len(positions)} 条")
    except Exception as e:
        print(f"迁移持仓数据失败: {e}")
    
    # 3. 迁移股票池
    try:
        stock_pool_file = os.path.join(base_dir, 'strategy', 'data', 'stock_pool.json')
        if os.path.exists(stock_pool_file):
            with open(stock_pool_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stocks = data.get('stocks', [])
                db.save_stock_pool(stocks)
                print(f"迁移股票池: {len(stocks)} 只股票")
    except Exception as e:
        print(f"迁移股票池失败: {e}")
    
    # 4. 迁移邮箱配置
    try:
        email_db_path = os.path.join(base_dir, 'backend', 'data', 'email_config.db')
        if os.path.exists(email_db_path):
            from email_config_manager import EmailConfigManager
            old_config = EmailConfigManager()
            config = old_config.get_config()
            recipients = config.pop('recipients', [])
            db.save_email_config(config)
            db.save_email_recipients(recipients)
            print(f"迁移邮箱配置: {config.get('sender_email', 'N/A')}")
    except Exception as e:
        print(f"迁移邮箱配置失败: {e}")
    
    # 5. 迁移价格缓存
    try:
        price_cache_file = os.path.join(base_dir, 'backend', 'data', 'price_cache.json')
        if os.path.exists(price_cache_file):
            with open(price_cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                db.save_price_cache(cache)
                print(f"迁移价格缓存: {len(cache)} 条")
    except Exception as e:
        print(f"迁移价格缓存失败: {e}")
    
    print("=== 数据迁移完成 ===")


if __name__ == '__main__':
    migrate_all_data()
    db = get_unified_db()
    print("\n=== 验证数据 ===")
    print(f"回测股票池: {db.get_backtest_pool()}")
    print(f"持仓数据: {len(db.get_positions())} 条")
    print(f"股票池: {len(db.get_stock_pool())} 只")
    print(f"邮箱配置: {db.get_email_config()}")
    print(f"收件人: {db.get_email_recipients()}")
