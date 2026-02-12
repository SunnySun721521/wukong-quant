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
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
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
    
    def get_config(self, key: str) -> Optional[str]:
        """获取配置值"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT config_value, config_type FROM email_config WHERE config_key = ?', (key,))
            result = cursor.fetchone()
            
            if result:
                value, config_type = result
                if config_type == 'json':
                    return json.loads(value)
                elif config_type == 'integer':
                    return int(value)
                elif config_type == 'boolean':
                    return value.lower() == 'true'
                else:
                    return value
            return None
    
    def set_config(self, key: str, value: Any, config_type: str = 'string', description: str = None):
        """设置配置值"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 将值转换为字符串
            if config_type == 'json':
                str_value = json.dumps(value, ensure_ascii=False)
            else:
                str_value = str(value)
            
            # 使用INSERT OR REPLACE来更新或插入配置
            cursor.execute('''
                INSERT OR REPLACE INTO email_config 
                (config_key, config_value, config_type, description, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (key, str_value, config_type, description))
            
            conn.commit()
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        config = {}
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT config_key, config_value, config_type FROM email_config')
            results = cursor.fetchall()
            
            for key, value, config_type in results:
                if config_type == 'json':
                    config[key] = json.loads(value)
                elif config_type == 'integer':
                    config[key] = int(value)
                elif config_type == 'boolean':
                    config[key] = value.lower() == 'true'
                else:
                    config[key] = value
            
            return config
    
    def delete_config(self, key: str):
        """删除配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM email_config WHERE config_key = ?', (key,))
            conn.commit()
    
    def log_email_send(self, log_id: str, task_id: str = None, pdf_file: str = None, 
                    status: str = None, recipients: List[Dict[str, Any]] = None, 
                    error_message: str = None, retry_count: int = 0):
        """记录邮件发送日志"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 将收件人列表转换为JSON字符串
            recipients_json = json.dumps(recipients, ensure_ascii=False) if recipients else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO email_send_log 
                (log_id, task_id, pdf_file, status, recipients, error_message, retry_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (log_id, task_id, pdf_file, status, recipients_json, error_message, retry_count))
            
            conn.commit()
    
    def get_email_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取邮件发送日志"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT log_id, task_id, pdf_file, status, recipients, error_message, 
                       retry_count, created_at
                FROM email_send_log
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            logs = []
            
            for row in results:
                log = {
                    'log_id': row[0],
                    'task_id': row[1],
                    'pdf_file': row[2],
                    'status': row[3],
                    'recipients': json.loads(row[4]) if row[4] else [],
                    'error_message': row[5],
                    'retry_count': row[6],
                    'timestamp': row[7]
                }
                logs.append(log)
            
            return logs
    
    def save_template(self, template_name: str, template_type: str, 
                   subject_template: str = None, body_template: str = None, 
                   description: str = None):
        """保存邮件模板"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO email_template
                (template_name, template_type, subject_template, body_template, description, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (template_name, template_type, subject_template, body_template, description))
            
            conn.commit()
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """获取邮件模板"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT template_name, template_type, subject_template, body_template, description
                FROM email_template
                WHERE template_name = ?
            ''', (template_name,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'template_name': result[0],
                    'template_type': result[1],
                    'subject_template': result[2],
                    'body_template': result[3],
                    'description': result[4]
                }
            return None
    
    def get_all_templates(self) -> List[Dict[str, Any]]:
        """获取所有邮件模板"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT template_name, template_type, subject_template, body_template, description
                FROM email_template
                ORDER BY template_name
            ''')
            
            results = cursor.fetchall()
            templates = []
            
            for row in results:
                template = {
                    'template_name': row[0],
                    'template_type': row[1],
                    'subject_template': row[2],
                    'body_template': row[3],
                    'description': row[4]
                }
                templates.append(template)
            
            return templates
    
    def init_default_config(self):
        """初始化默认配置"""
        default_config = {
            'enabled': ('true', 'boolean', '是否启用邮件发送'),
            'sender_email': ('', 'string', '发送邮箱地址'),
            'sender_auth_code': ('', 'string', '发送邮箱授权码'),
            'smtp_server': ('smtp.qq.com', 'string', 'SMTP服务器地址'),
            'smtp_port': ('465', 'integer', 'SMTP服务器端口'),
            'use_ssl': ('true', 'boolean', '是否使用SSL'),
            'timeout': ('30', 'integer', '连接超时时间(秒)'),
            'retry_times': ('3', 'integer', '重试次数'),
            'retry_interval': ('5', 'integer', '重试间隔(秒)'),
            'email_subject_template': ('每日操作计划 - {date}', 'string', '邮件主题模板'),
            'email_body_template': ('simple', 'string', '邮件正文模板'),
            'recipients': ('[]', 'json', '收件人列表')
        }
        
        for key, (value, config_type, description) in default_config.items():
            if self.get_config(key) is None:
                self.set_config(key, value, config_type, description)
    
    def init_default_templates(self):
        """初始化默认模板"""
        default_templates = [
            {
                'template_name': 'simple',
                'template_type': 'text',
                'subject_template': '每日操作计划 - {date}',
                'body_template': '您好！\n\n附件是今日的操作计划PDF文件，请查收。\n\n市场状态：{market_status}\n当前仓位：{current_position}\n总资产：{total_assets}\n\n发送时间：{datetime}\n\n祝好！',
                'description': '简单文本模板'
            },
            {
                'template_name': 'detailed',
                'template_type': 'html',
                'subject_template': '每日操作计划 - {date}',
                'body_template': '<!DOCTYPE html><html><head><meta charset="utf-8"><title>每日操作计划</title></head><body><h2>每日操作计划</h2><p>您好！</p><p>附件是今日的操作计划PDF文件，请查收。</p><table border="1"><tr><td>市场状态</td><td>{market_status}</td></tr><tr><td>当前仓位</td><td>{current_position}</td></tr><tr><td>总资产</td><td>{total_assets}</td></tr></table><p>发送时间：{datetime}</p><p>祝好！</p></body></html>',
                'description': 'HTML详细模板'
            }
        ]
        
        for template in default_templates:
            if self.get_template(template['template_name']) is None:
                self.save_template(**template)
    
    # 接收邮箱地址管理方法
    def add_recipient(self, email_address: str, name: str = None, description: str = None, is_active: bool = True) -> bool:
        """添加接收邮箱地址"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO email_recipients (email_address, name, description, is_active)
                    VALUES (?, ?, ?, ?)
                ''', (email_address, name, description, is_active))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            print(f"邮箱地址 {email_address} 已存在")
            return False
        except Exception as e:
            print(f"添加接收邮箱失败: {e}")
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