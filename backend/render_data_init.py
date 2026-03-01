# -*- coding: utf-8 -*-
"""
Render 数据初始化模块
在 Render 环境启动时自动初始化必要的数据文件
"""
import os
import csv
import json
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'wukong_data.db')

DEFAULT_POSITIONS = [
    {
        'symbol': '002009',
        'name': '天奇股份',
        'shares': 1000,
        'quantity': 1000,
        'cost_price': 15.50,
        'current_price': 15.50,
        'change_pct': 0.00,
        'market_value': 15500,
        'profit_loss': 0,
        'profit_pct': 0.00,
        'profit_loss_percent': 0.00
    }
]

DEFAULT_BACKTEST_POOL = [
    "002009", "002371", "300750", "600519", "000858", "600036", 
    "601318", "601398", "000333", "600104", "600050", "601288", 
    "600009", "600016", "600030", "601012", "601888", "603259", 
    "603501", "002594", "000001", "300059", "600887", "601166"
]

DEFAULT_EMAIL_CONFIG = {
    'sender_email': '25285603@qq.com',
    'sender_auth_code': 'xqlznzjdrqynbjbc',
    'smtp_server': 'smtp.qq.com',
    'smtp_port': '465',
    'use_ssl': 'true',
    'enabled': 'true'
}

DEFAULT_RECIPIENTS = ['25285603@qq.com', 'lib@tcscd.com']


def ensure_database():
    """确保数据库存在并初始化表结构"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                name TEXT,
                shares INTEGER DEFAULT 0,
                quantity INTEGER DEFAULT 0,
                cost_price REAL DEFAULT 0,
                current_price REAL DEFAULT 0,
                change_pct REAL DEFAULT 0,
                market_value REAL DEFAULT 0,
                profit_loss REAL DEFAULT 0,
                profit_pct REAL DEFAULT 0,
                profit_loss_percent REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_pool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL UNIQUE,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT NOT NULL UNIQUE,
                config_value TEXT,
                config_type TEXT DEFAULT 'string',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_address TEXT NOT NULL UNIQUE,
                is_active INTEGER DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    
    print(f"数据库初始化完成: {DB_PATH}")


def init_positions():
    """初始化持仓数据"""
    csv_path = os.path.join(BASE_DIR, 'strategy', 'data', 'position_data.csv')
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM positions")
        db_count = cursor.fetchone()[0]
        
        if db_count == 0:
            for pos in DEFAULT_POSITIONS:
                cursor.execute('''
                    INSERT INTO positions 
                    (symbol, name, shares, quantity, cost_price, current_price, 
                     change_pct, market_value, profit_loss, profit_pct, profit_loss_percent, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (pos['symbol'], pos['name'], pos['shares'], pos['quantity'],
                      pos['cost_price'], pos['current_price'], pos['change_pct'],
                      pos['market_value'], pos['profit_loss'], pos['profit_pct'],
                      pos['profit_loss_percent'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            print(f"已初始化 {len(DEFAULT_POSITIONS)} 条默认持仓数据到数据库")
    
    if not os.path.exists(csv_path):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['symbol', 'name', 'quantity', 'cost_price', 'current_price', 
                         'profit_loss', 'profit_loss_percent']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for pos in DEFAULT_POSITIONS:
                writer.writerow({
                    'symbol': pos['symbol'],
                    'name': pos['name'],
                    'quantity': pos['quantity'],
                    'cost_price': pos['cost_price'],
                    'current_price': pos['current_price'],
                    'profit_loss': pos['profit_loss'],
                    'profit_loss_percent': pos['profit_loss_percent']
                })
        print(f"已创建持仓CSV文件: {csv_path}")


def init_backtest_pool():
    """初始化回测股票池"""
    json_path = os.path.join(BASE_DIR, 'strategy', 'data', 'backtest_pool.json')
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM backtest_pool")
        db_count = cursor.fetchone()[0]
        
        if db_count == 0:
            for stock in DEFAULT_BACKTEST_POOL:
                cursor.execute('''
                    INSERT OR IGNORE INTO backtest_pool (stock_code)
                    VALUES (?)
                ''', (stock,))
            conn.commit()
            print(f"已初始化 {len(DEFAULT_BACKTEST_POOL)} 只默认股票到回测池")
    
    if not os.path.exists(json_path):
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'stocks': DEFAULT_BACKTEST_POOL,
                'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }, f, ensure_ascii=False)
        print(f"已创建回测股票池文件: {json_path}")


def init_email_config():
    """初始化邮箱配置 - 同时初始化两个数据库"""
    # 1. 初始化 wukong_data.db
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM email_config")
        db_count = cursor.fetchone()[0]
        
        if db_count == 0:
            for key, value in DEFAULT_EMAIL_CONFIG.items():
                config_type = 'boolean' if value.lower() in ['true', 'false'] else 'string'
                cursor.execute('''
                    INSERT INTO email_config (config_key, config_value, config_type, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (key, value, config_type, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            for email in DEFAULT_RECIPIENTS:
                cursor.execute('''
                    INSERT OR IGNORE INTO email_recipients (email_address)
                    VALUES (?)
                ''', (email,))
            
            conn.commit()
            print(f"已初始化邮箱配置到 wukong_data.db")
    
    # 2. 初始化 email_config.db (email_config_db.py 使用的数据库)
    email_db_path = os.path.join(DATA_DIR, 'email_config.db')
    try:
        with sqlite3.connect(email_db_path) as conn:
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE NOT NULL,
                    config_value TEXT NOT NULL,
                    config_type TEXT NOT NULL DEFAULT 'string',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_address TEXT UNIQUE NOT NULL,
                    name TEXT,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 检查是否已有配置
            cursor.execute("SELECT COUNT(*) FROM email_config")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # 插入默认配置
                for key, value in DEFAULT_EMAIL_CONFIG.items():
                    config_type = 'boolean' if value.lower() in ['true', 'false'] else 'string'
                    desc = {
                        'sender_email': '发送邮箱地址',
                        'sender_auth_code': '发送邮箱授权码',
                        'smtp_server': 'SMTP服务器地址',
                        'smtp_port': 'SMTP服务器端口',
                        'use_ssl': '是否使用SSL',
                        'enabled': '是否启用邮件发送'
                    }.get(key, key)
                    cursor.execute('''
                        INSERT INTO email_config (config_key, config_value, config_type, description)
                        VALUES (?, ?, ?, ?)
                    ''', (key, value, config_type, desc))
                
                # 插入默认收件人
                for email in DEFAULT_RECIPIENTS:
                    cursor.execute('''
                        INSERT OR IGNORE INTO email_recipients (email_address)
                        VALUES (?)
                    ''', (email,))
                
                conn.commit()
                print(f"已初始化邮箱配置到 email_config.db")
            else:
                # 确保关键配置存在
                for key, value in DEFAULT_EMAIL_CONFIG.items():
                    cursor.execute("SELECT config_value FROM email_config WHERE config_key = ?", (key,))
                    if not cursor.fetchone():
                        config_type = 'boolean' if value.lower() in ['true', 'false'] else 'string'
                        cursor.execute('''
                            INSERT INTO email_config (config_key, config_value, config_type)
                            VALUES (?, ?, ?)
                        ''', (key, value, config_type))
                conn.commit()
                print(f"email_config.db 配置已验证")
                
    except Exception as e:
        print(f"初始化 email_config.db 失败: {e}")
        import traceback
        traceback.print_exc()


def init_render_data():
    """Render 环境数据初始化入口"""
    print("=" * 50)
    print("Render 数据初始化开始")
    print("=" * 50)
    
    ensure_database()
    init_positions()
    init_backtest_pool()
    init_email_config()
    
    print("=" * 50)
    print("Render 数据初始化完成")
    print("=" * 50)


def get_db_positions():
    """从数据库获取持仓数据"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM positions ORDER BY symbol")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"从数据库获取持仓失败: {e}")
        return []


if __name__ == '__main__':
    init_render_data()
    
    print("\n验证数据:")
    positions = get_db_positions()
    for pos in positions:
        print(f"  {pos.get('symbol')} {pos.get('name')}: {pos.get('shares')}股")
