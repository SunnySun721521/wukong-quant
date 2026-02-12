#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from email_config_db import EmailConfigDB

class EmailConfigManager:
    """邮件配置管理类"""
    
    def __init__(self, db_path: str = None):
        self.db = EmailConfigDB(db_path)
        # 初始化默认配置和模板
        self.db.init_default_config()
        self.db.init_default_templates()
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前邮件配置"""
        config = self.db.get_all_config()
        
        # 从email_recipients表动态获取收件人列表
        recipients = self.db.get_recipients(active_only=True)
        config['recipients'] = [recipient['email_address'] for recipient in recipients]
        
        return config
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """更新邮件配置"""
        try:
            for key, value in config.items():
                if key == 'recipients':
                    self.db.set_config(key, value, 'json', '收件人列表')
                elif key in ['enabled', 'use_ssl']:
                    self.db.set_config(key, value, 'boolean', f'是否{"启用" if value else "禁用"}相关功能')
                elif key in ['smtp_port', 'retry_times', 'retry_interval', 'timeout']:
                    self.db.set_config(key, value, 'integer', f'{key}配置值')
                else:
                    self.db.set_config(key, value, 'string', f'{key}配置值')
            return True
        except Exception as e:
            print(f"更新邮件配置失败: {e}")
            return False
    
    def validate_config(self) -> tuple[bool, Optional[str]]:
        """验证配置的完整性和有效性"""
        config = self.get_config()
        
        if not config.get('enabled', False):
            return True, None
        
        if not config.get('sender_email'):
            return False, '发送邮箱地址未配置'
        
        if not config.get('sender_auth_code'):
            return False, '邮箱授权码未配置'
        
        recipients = config.get('recipients', [])
        if not recipients:
            return False, '接收邮箱列表为空'
        
        for recipient in recipients:
            if not self.validate_email_address(recipient):
                return False, f'接收邮箱地址格式错误: {recipient}'
        
        return True, None
    
    @staticmethod
    def validate_email_address(email: str) -> bool:
        """验证邮箱地址格式"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """获取邮件模板"""
        return self.db.get_template(template_name)
    
    def get_all_templates(self) -> List[Dict[str, Any]]:
        """获取所有邮件模板"""
        return self.db.get_all_templates()
    
    def save_template(self, template_name: str, template_type: str, 
                   subject_template: str = None, body_template: str = None, 
                   description: str = None) -> bool:
        """保存邮件模板"""
        try:
            self.db.save_template(template_name, template_type, subject_template, body_template, description)
            return True
        except Exception as e:
            print(f"保存邮件模板失败: {e}")
            return False
    
    def log_email_send(self, log_id: str, task_id: str = None, pdf_file: str = None, 
                    status: str = None, recipients: List[Dict[str, Any]] = None, 
                    error_message: str = None, retry_count: int = 0):
        """记录邮件发送日志"""
        try:
            self.db.log_email_send(log_id, task_id, pdf_file, status, recipients, error_message, retry_count)
            return True
        except Exception as e:
            print(f"记录邮件发送日志失败: {e}")
            return False
    
    def get_email_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取邮件发送日志"""
        try:
            return self.db.get_email_logs(limit)
        except Exception as e:
            print(f"获取邮件发送日志失败: {e}")
            return []
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置（保留此方法以兼容旧代码）"""
        return {
            'enabled': False,
            'sender_email': '',
            'sender_auth_code': '',
            'recipients': [],
            'smtp_server': 'smtp.qq.com',
            'smtp_port': 465,
            'use_ssl': True,
            'email_subject_template': '每日操作计划 - {date}',
            'email_body_template': 'simple',
            'retry_times': 3,
            'retry_interval': 5,
            'timeout': 30
        }