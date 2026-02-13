#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class EmailConfigDB:
    """邮件配置数据库管理类"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'data', 'email_config.db')
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            print(f"初始化数据库: {self.db_path}")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建邮件配置表
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
                
                # 创建邮件发送日志表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_send_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        log_id TEXT UNIQUE NOT NULL,
                        task_id TEXT,
                        pdf_file TEXT,
                        status TEXT NOT NULL,
                        recipients TEXT,
                        error_message TEXT,
                        retry_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建邮件模板表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_template (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_name TEXT UNIQUE NOT NULL,
                        template_type TEXT NOT NULL,
                        subject_template TEXT,
                        body_template TEXT,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建接收邮箱地址表
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
                
                # 创建邮件发送计划表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_send_schedule (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        schedule_name TEXT UNIQUE NOT NULL,
                        schedule_type TEXT NOT NULL,
                        schedule_config TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                print("数据库初始化完成")
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """测试数据库连接"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                # 测试接收邮箱表
                cursor.execute("SELECT COUNT(*) FROM email_recipients")
                recipient_count = cursor.fetchone()[0]
                
                return {
                    'database_path': self.db_path,
                    'tables': [table[0] for table in tables],
                    'recipient_count': recipient_count,
                    'status': 'success'
                }
        except Exception as e:
            return {
                'database_path': self.db_path,
                'error': str(e),
                'status': 'error'
            }
    
    def get_config(self, key: str) -> Optional[str]:
        """获取配置值"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT config_value FROM email_config WHERE config_key = ?", (key,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"获取配置失败: {e}")
            return None
    
    def set_config(self, key: str, value: str, config_type: str = 'string', description: str = None) -> bool:
        """设置配置值"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO email_config 
                    (config_key, config_value, config_type, description, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (key, value, config_type, description))
                conn.commit()
                return True
        except Exception as e:
            print(f"设置配置失败: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM email_config")
                rows = cursor.fetchall()
                
                config = {}
                for row in rows:
                    key = row['config_key']
                    value = row['config_value']
                    config_type = row['config_type']
                    
                    if config_type == 'boolean':
                        config[key] = value.lower() == 'true'
                    elif config_type == 'integer':
                        config[key] = int(value)
                    elif config_type == 'json':
                        import json
                        config[key] = json.loads(value)
                    else:
                        config[key] = value
                
                return config
        except Exception as e:
            print(f"获取所有配置失败: {e}")
            return {}
    
    # 接收邮箱地址管理方法
    def add_recipient(self, email_address: str, name: str = None, description: str = None, is_active: bool = True) -> bool:
        """添加接收邮箱地址"""
        try:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO email_recipients (email_address, name, description, is_active)
                    VALUES (?, ?, ?, ?)
                ''', (email_address, name, description, is_active))
                conn.commit()
                print(f"成功添加接收邮箱: {email_address}")
                return True
        except sqlite3.IntegrityError as e:
            error_msg = f"邮箱地址 {email_address} 已存在"
            print(error_msg)
            return False
        except sqlite3.Error as e:
            error_msg = f"数据库错误: {str(e)}"
            print(f"添加接收邮箱失败: {error_msg}")
            return False
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(f"添加接收邮箱失败: {error_msg}")
            return False
    
    def get_recipients(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """获取接收邮箱列表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if active_only:
                    cursor.execute('SELECT * FROM email_recipients WHERE is_active = 1 ORDER BY email_address')
                else:
                    cursor.execute('SELECT * FROM email_recipients ORDER BY email_address')
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"获取接收邮箱列表失败: {e}")
            return []
    
    def update_recipient(self, id: int, email_address: str = None, name: str = None, 
                        description: str = None, is_active: bool = None) -> bool:
        """更新接收邮箱信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 构建更新语句
                updates = []
                params = []
                
                if email_address is not None:
                    updates.append("email_address = ?")
                    params.append(email_address)
                if name is not None:
                    updates.append("name = ?")
                    params.append(name)
                if description is not None:
                    updates.append("description = ?")
                    params.append(description)
                if is_active is not None:
                    updates.append("is_active = ?")
                    params.append(is_active)
                
                if not updates:
                    return False
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(id)
                
                cursor.execute(f'''
                    UPDATE email_recipients 
                    SET {', '.join(updates)}
                    WHERE id = ?
                ''', params)
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"更新接收邮箱失败: {e}")
            return False
    
    def delete_recipient(self, id: int) -> bool:
        """删除接收邮箱"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM email_recipients WHERE id = ?', (id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"删除接收邮箱失败: {e}")
            return False
    
    def clear_recipients(self) -> bool:
        """清空所有接收邮箱"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM email_recipients')
                conn.commit()
                return True
        except Exception as e:
            print(f"清空接收邮箱失败: {e}")
            return False
    
    def get_recipient_by_email(self, email_address: str) -> Optional[Dict[str, Any]]:
        """根据邮箱地址获取接收邮箱信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM email_recipients WHERE email_address = ?', (email_address,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"获取接收邮箱信息失败: {e}")
            return None