# -*- coding: utf-8 -*-
"""
完整数据迁移脚本
将所有本地缓存数据迁移到统一数据库
"""
import os
import sys
import json
import csv
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'wukong_data.db')

def ensure_db():
    """确保数据库存在并创建表结构"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                name TEXT,
                shares INTEGER DEFAULT 0,
                cost_price REAL DEFAULT 0,
                current_price REAL DEFAULT 0,
                change_pct REAL DEFAULT 0,
                market_value REAL DEFAULT 0,
                profit_loss REAL DEFAULT 0,
                profit_pct REAL DEFAULT 0,
                quantity INTEGER DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS stock_pool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                stock_name TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_address TEXT NOT NULL UNIQUE,
                is_active INTEGER DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT NOT NULL UNIQUE,
                config_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print(f"数据库初始化完成: {DB_PATH}")


def migrate_positions():
    """迁移持仓数据"""
    csv_path = os.path.join(BASE_DIR, 'strategy', 'data', 'position_data.csv')
    
    if not os.path.exists(csv_path):
        print("持仓CSV文件不存在，创建默认数据...")
        positions = [{
            'symbol': '002009',
            'name': '天奇股份',
            'shares': 1000,
            'cost_price': 15.50,
            'current_price': 15.50,
            'change_pct': 0.00,
            'market_value': 15500,
            'profit_loss': 0,
            'profit_pct': 0.00
        }]
    else:
        positions = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                positions.append(row)
    
    if not positions:
        print("没有持仓数据需要迁移")
        return
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        for pos in positions:
            symbol = pos.get('symbol', '')
            name = pos.get('name', '')
            shares = int(pos.get('shares', pos.get('quantity', 0)))
            cost_price = float(pos.get('cost_price', 0))
            current_price = float(pos.get('current_price', 0))
            change_pct = float(pos.get('change_pct', 0))
            market_value = float(pos.get('market_value', 0))
            profit_loss = float(pos.get('profit_loss', 0))
            profit_pct = float(pos.get('profit_pct', 0))
            
            cursor.execute('''
                INSERT OR REPLACE INTO positions 
                (symbol, name, shares, cost_price, current_price, change_pct, 
                 market_value, profit_loss, profit_pct, quantity, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, name, shares, cost_price, current_price, change_pct,
                  market_value, profit_loss, profit_pct, shares,
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
    
    print(f"已迁移 {len(positions)} 条持仓数据")
    for pos in positions:
        print(f"  {pos.get('symbol')} {pos.get('name')}: {pos.get('shares')}股")


def migrate_backtest_pool():
    """迁移回测股票池"""
    json_path = os.path.join(BASE_DIR, 'strategy', 'data', 'backtest_pool.json')
    
    default_pool = ["002009", "002371", "300750", "600519", "000858", "600036", 
                   "601318", "601398", "000333", "600104", "600050", "601288", 
                   "600009", "600016", "600030", "601012", "601888", "603259", 
                   "603501", "002594", "000001", "300059", "600887", "601166"]
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            stocks = data.get('stocks', default_pool)
    else:
        stocks = default_pool
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        for stock in stocks:
            cursor.execute('''
                INSERT OR IGNORE INTO backtest_pool (stock_code)
                VALUES (?)
            ''', (stock,))
        
        conn.commit()
    
    print(f"已迁移 {len(stocks)} 只回测股票")


def migrate_email_config():
    """迁移邮箱配置"""
    email_db_path = os.path.join(BASE_DIR, 'backend', 'data', 'email_config.db')
    
    default_config = {
        'sender_email': '25285603@qq.com',
        'sender_auth_code': 'xqlznzjdrqynbjbc',
        'smtp_server': 'smtp.qq.com',
        'smtp_port': '465',
        'use_ssl': 'true',
        'enabled': 'true'
    }
    
    default_recipients = ['25285603@qq.com', 'lib@tcscd.com']
    
    if os.path.exists(email_db_path):
        try:
            old_conn = sqlite3.connect(email_db_path)
            old_cursor = old_conn.cursor()
            
            old_cursor.execute("SELECT config_key, config_value, config_type FROM email_config")
            rows = old_cursor.fetchall()
            
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                
                for key, value, config_type in rows:
                    cursor.execute('''
                        INSERT OR REPLACE INTO email_config 
                        (config_key, config_value, config_type, updated_at)
                        VALUES (?, ?, ?, ?)
                    ''', (key, value, config_type, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                conn.commit()
            
            old_conn.close()
            print("已迁移邮箱配置")
            
        except Exception as e:
            print(f"迁移邮箱配置失败: {e}")
    else:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            for key, value in default_config.items():
                config_type = 'boolean' if value.lower() in ['true', 'false'] else 'string'
                cursor.execute('''
                    INSERT OR REPLACE INTO email_config 
                    (config_key, config_value, config_type, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (key, value, config_type, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            for email in default_recipients:
                cursor.execute('''
                    INSERT OR IGNORE INTO email_recipients (email_address)
                    VALUES (?)
                ''', (email,))
            
            conn.commit()
        
        print("已创建默认邮箱配置")


def verify_migration():
    """验证迁移结果"""
    print("\n=== 验证迁移结果 ===")
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM positions")
        pos_count = cursor.fetchone()[0]
        print(f"持仓数据: {pos_count} 条")
        
        cursor.execute("SELECT COUNT(*) FROM backtest_pool")
        pool_count = cursor.fetchone()[0]
        print(f"回测股票池: {pool_count} 只")
        
        cursor.execute("SELECT COUNT(*) FROM email_config")
        config_count = cursor.fetchone()[0]
        print(f"邮箱配置: {config_count} 项")
        
        cursor.execute("SELECT COUNT(*) FROM email_recipients")
        recipient_count = cursor.fetchone()[0]
        print(f"收件人: {recipient_count} 个")
        
        cursor.execute("SELECT symbol, name, shares FROM positions")
        print("\n持仓详情:")
        for row in cursor.fetchall():
            print(f"  {row[0]} {row[1]}: {row[2]}股")


def main():
    print("=" * 50)
    print("开始数据迁移")
    print("=" * 50)
    print(f"数据库路径: {DB_PATH}")
    
    ensure_db()
    migrate_positions()
    migrate_backtest_pool()
    migrate_email_config()
    verify_migration()
    
    print("\n" + "=" * 50)
    print("数据迁移完成!")
    print("=" * 50)
    print(f"\n请将以下文件添加到Git:")
    print(f"  {DB_PATH}")
    print("\n执行命令:")
    print("  git add data/wukong_data.db")
    print("  git commit -m 'Add unified database'")
    print("  git push origin main")


if __name__ == '__main__':
    main()
