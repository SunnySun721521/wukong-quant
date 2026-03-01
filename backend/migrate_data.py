# -*- coding: utf-8 -*-
"""
数据迁移工具 - 用于将现有缓存数据迁移到统一数据库
使用方法: python migrate_data.py
"""
import os
import sys
import json
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_database import get_unified_db, UnifiedDatabase

def migrate_all_data():
    """迁移所有现有数据到统一数据库"""
    print("=" * 50)
    print("开始数据迁移")
    print("=" * 50)
    
    db = get_unified_db()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    migrated_count = 0
    
    # 1. 迁移回测股票池
    try:
        backtest_pool_file = os.path.join(base_dir, 'strategy', 'data', 'backtest_pool.json')
        if os.path.exists(backtest_pool_file):
            with open(backtest_pool_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stocks = data.get('stocks', [])
                if stocks:
                    db.save_backtest_pool(stocks)
                    print(f"✓ 迁移回测股票池: {len(stocks)} 只股票")
                    print(f"  股票列表: {stocks}")
                    migrated_count += 1
        else:
            print(f"○ 回测股票池文件不存在: {backtest_pool_file}")
    except Exception as e:
        print(f"✗ 迁移回测股票池失败: {e}")
    
    # 2. 迁移持仓数据
    try:
        position_file = os.path.join(base_dir, 'strategy', 'data', 'position_data.csv')
        if os.path.exists(position_file):
            positions = []
            with open(position_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    positions.append({
                        'symbol': row.get('symbol', ''),
                        'name': row.get('name', ''),
                        'shares': int(row.get('shares', 0)),
                        'cost_price': float(row.get('cost_price', 0)),
                        'current_price': float(row.get('current_price', 0)),
                        'change_pct': float(row.get('change_pct', 0)),
                        'market_value': float(row.get('market_value', 0)),
                        'profit_loss': float(row.get('profit_loss', 0)),
                        'profit_pct': float(row.get('profit_pct', 0))
                    })
            if positions:
                db.save_positions(positions)
                print(f"✓ 迁移持仓数据: {len(positions)} 条")
                for pos in positions:
                    print(f"  - {pos['symbol']} {pos['name']}: {pos['shares']}股")
                migrated_count += 1
    except Exception as e:
        print(f"✗ 迁移持仓数据失败: {e}")
    
    # 3. 迁移股票池
    try:
        stock_pool_file = os.path.join(base_dir, 'strategy', 'data', 'stock_pool.json')
        if os.path.exists(stock_pool_file):
            with open(stock_pool_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stocks = data.get('stocks', [])
                if stocks:
                    db.save_stock_pool(stocks)
                    print(f"✓ 迁移股票池: {len(stocks)} 只股票")
                    migrated_count += 1
    except Exception as e:
        print(f"✗ 迁移股票池失败: {e}")
    
    # 4. 迁移邮箱配置
    try:
        email_db_path = os.path.join(base_dir, 'backend', 'data', 'email_config.db')
        if os.path.exists(email_db_path):
            import sqlite3
            conn = sqlite3.connect(email_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT config_key, config_value, config_type FROM email_config")
            rows = cursor.fetchall()
            conn.close()
            
            config = {}
            for key, value, config_type in rows:
                if config_type == 'boolean':
                    config[key] = value.lower() == 'true' if value else False
                elif config_type == 'integer':
                    config[key] = int(value) if value else 0
                elif config_type == 'json':
                    config[key] = json.loads(value) if value else []
                else:
                    config[key] = value
            
            if config:
                db.save_email_config(config)
                recipients = config.pop('recipients', [])
                db.save_email_recipients(recipients)
                print(f"✓ 迁移邮箱配置")
                print(f"  发件人: {config.get('sender_email', 'N/A')}")
                print(f"  授权码: {config.get('sender_auth_code', 'N/A')}")
                print(f"  收件人: {recipients}")
                migrated_count += 1
    except Exception as e:
        print(f"✗ 迁移邮箱配置失败: {e}")
    
    # 5. 迁移价格缓存
    try:
        price_cache_file = os.path.join(base_dir, 'backend', 'data', 'price_cache.json')
        if os.path.exists(price_cache_file):
            with open(price_cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                if cache:
                    db.save_price_cache(cache)
                    print(f"✓ 迁移价格缓存: {len(cache)} 条")
                    migrated_count += 1
    except Exception as e:
        print(f"✗ 迁移价格缓存失败: {e}")
    
    # 6. 迁移现金配置
    try:
        cash_config_file = os.path.join(base_dir, 'backend', 'data', 'cash_config.json')
        if os.path.exists(cash_config_file):
            with open(cash_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config:
                    db.save_cash_config(config)
                    print(f"✓ 迁移现金配置: {config}")
                    migrated_count += 1
    except Exception as e:
        print(f"✗ 迁移现金配置失败: {e}")
    
    print("=" * 50)
    print(f"数据迁移完成! 共迁移 {migrated_count} 项数据")
    print("=" * 50)
    
    return migrated_count


def show_current_data():
    """显示当前数据库中的数据"""
    print("\n" + "=" * 50)
    print("当前统一数据库中的数据")
    print("=" * 50)
    
    db = get_unified_db()
    
    # 回测股票池
    pool = db.get_backtest_pool()
    print(f"\n回测股票池 ({len(pool)}只):")
    print(f"  {pool}")
    
    # 持仓数据
    positions = db.get_positions()
    print(f"\n持仓数据 ({len(positions)}条):")
    for pos in positions:
        print(f"  {pos.get('symbol')} {pos.get('name')}: {pos.get('shares')}股")
    
    # 股票池
    stock_pool = db.get_stock_pool()
    print(f"\n股票池 ({len(stock_pool)}只):")
    for sp in stock_pool[:10]:
        print(f"  {sp.get('stock_code')} {sp.get('stock_name')}")
    
    # 邮箱配置
    email_config = db.get_email_config()
    print(f"\n邮箱配置:")
    for key, value in email_config.items():
        if 'code' in key.lower() or 'password' in key.lower():
            print(f"  {key}: ****")
        else:
            print(f"  {key}: {value}")
    
    # 收件人
    recipients = db.get_email_recipients()
    print(f"\n收件人: {recipients}")
    
    # 价格缓存
    price_cache = db.get_price_cache()
    print(f"\n价格缓存 ({len(price_cache)}条):")
    for symbol, data in list(price_cache.items())[:5]:
        print(f"  {symbol}: {data.get('price')}")
    
    print("\n" + "=" * 50)


if __name__ == '__main__':
    migrate_all_data()
    show_current_data()
