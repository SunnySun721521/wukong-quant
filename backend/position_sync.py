# -*- coding: utf-8 -*-
"""
持仓数据同步适配器
在不修改现有代码的情况下，实现本地CSV与数据库的双向同步
确保 Render 平台和本地程序数据一致
"""
import os
import csv
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class PositionDataSync:
    """持仓数据同步管理器"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.csv_path = os.path.join(self.base_dir, 'strategy', 'data', 'position_data.csv')
        self.db_path = os.path.join(self.base_dir, 'data', 'wukong_data.db')
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """确保数据库和表存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
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
            conn.commit()
    
    def csv_to_db(self) -> bool:
        """将CSV数据同步到数据库"""
        try:
            if not os.path.exists(self.csv_path):
                print(f"CSV文件不存在: {self.csv_path}")
                return False
            
            positions = []
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    positions.append(row)
            
            if not positions:
                print("CSV文件为空")
                return False
            
            with sqlite3.connect(self.db_path) as conn:
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
                    quantity = int(pos.get('quantity', shares))
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO positions 
                        (symbol, name, shares, cost_price, current_price, change_pct, 
                         market_value, profit_loss, profit_pct, quantity, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (symbol, name, shares, cost_price, current_price, change_pct,
                          market_value, profit_loss, profit_pct, quantity, 
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                conn.commit()
            
            print(f"已同步 {len(positions)} 条持仓数据到数据库")
            return True
            
        except Exception as e:
            print(f"CSV同步到数据库失败: {e}")
            return False
    
    def db_to_csv(self) -> bool:
        """将数据库数据同步到CSV"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM positions ORDER BY symbol")
                rows = cursor.fetchall()
            
            if not rows:
                print("数据库中没有持仓数据")
                return False
            
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            
            with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['symbol', 'name', 'shares', 'cost_price', 'current_price', 
                             'change_pct', 'market_value', 'profit_loss', 'profit_pct']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in rows:
                    writer.writerow({
                        'symbol': row['symbol'],
                        'name': row['name'],
                        'shares': row['shares'],
                        'cost_price': row['cost_price'],
                        'current_price': row['current_price'],
                        'change_pct': row['change_pct'],
                        'market_value': row['market_value'],
                        'profit_loss': row['profit_loss'],
                        'profit_pct': row['profit_pct']
                    })
            
            print(f"已同步 {len(rows)} 条持仓数据到CSV")
            return True
            
        except Exception as e:
            print(f"数据库同步到CSV失败: {e}")
            return False
    
    def get_positions(self) -> List[Dict]:
        """获取持仓数据（优先从数据库）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM positions ORDER BY symbol")
                rows = cursor.fetchall()
                
                if rows:
                    return [dict(row) for row in rows]
        except Exception as e:
            print(f"从数据库获取持仓失败: {e}")
        
        if os.path.exists(self.csv_path):
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        
        return []
    
    def save_positions(self, positions: List[Dict]) -> bool:
        """保存持仓数据（同时保存到数据库和CSV）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM positions")
                
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
                    quantity = int(pos.get('quantity', shares))
                    
                    cursor.execute('''
                        INSERT INTO positions 
                        (symbol, name, shares, cost_price, current_price, change_pct, 
                         market_value, profit_loss, profit_pct, quantity, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (symbol, name, shares, cost_price, current_price, change_pct,
                          market_value, profit_loss, profit_pct, quantity,
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                conn.commit()
            
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['symbol', 'name', 'shares', 'cost_price', 'current_price', 
                             'change_pct', 'market_value', 'profit_loss', 'profit_pct']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for pos in positions:
                    writer.writerow({k: pos.get(k, '') for k in fieldnames})
            
            print(f"已保存 {len(positions)} 条持仓数据")
            return True
            
        except Exception as e:
            print(f"保存持仓数据失败: {e}")
            return False
    
    def init_default_positions(self) -> bool:
        """初始化默认持仓数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM positions")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"数据库已有 {count} 条持仓数据")
                    return True
            
            default_positions = [
                {
                    'symbol': '002009',
                    'name': '天奇股份',
                    'shares': 1000,
                    'cost_price': 15.50,
                    'current_price': 15.50,
                    'change_pct': 0.00,
                    'market_value': 15500,
                    'profit_loss': 0,
                    'profit_pct': 0.00
                }
            ]
            
            self.save_positions(default_positions)
            print("已初始化默认持仓数据")
            return True
            
        except Exception as e:
            print(f"初始化默认持仓失败: {e}")
            return False


_sync_instance = None

def get_position_sync() -> PositionDataSync:
    """获取持仓数据同步实例"""
    global _sync_instance
    if _sync_instance is None:
        _sync_instance = PositionDataSync()
    return _sync_instance


def sync_on_startup():
    """启动时同步数据"""
    sync = get_position_sync()
    
    if os.path.exists(sync.csv_path):
        sync.csv_to_db()
        print("启动同步: CSV -> 数据库")
    else:
        sync.init_default_positions()
        print("启动同步: 初始化默认数据")


if __name__ == '__main__':
    sync = PositionDataSync()
    
    print("=== 持仓数据同步测试 ===")
    print(f"CSV路径: {sync.csv_path}")
    print(f"数据库路径: {sync.db_path}")
    
    if os.path.exists(sync.csv_path):
        print("\nCSV文件存在，同步到数据库...")
        sync.csv_to_db()
    
    print("\n当前持仓数据:")
    positions = sync.get_positions()
    for pos in positions:
        print(f"  {pos.get('symbol')} {pos.get('name')}: {pos.get('shares')}股")
