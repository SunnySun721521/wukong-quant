#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
邮件配置数据库初始化脚本
用于将现有的JSON配置迁移到数据库中
"""

import os
import json
from email_config_db import EmailConfigDB

def migrate_json_to_db():
    """将JSON配置迁移到数据库"""
    # 数据库路径
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'email_config.db')
    db = EmailConfigDB(db_path)
    
    # JSON配置文件路径
    json_config_path = os.path.join(os.path.dirname(__file__), 'data', 'email_config.json')
    
    # 如果JSON配置文件存在，则迁移配置
    if os.path.exists(json_config_path):
        try:
            with open(json_config_path, 'r', encoding='utf-8') as f:
                json_config = json.load(f)
            
            print(f"发现JSON配置文件，开始迁移配置到数据库...")
            
            # 迁移配置
            for key, value in json_config.items():
                if key == 'recipients':
                    db.set_config(key, value, 'json', '收件人列表')
                elif key in ['enabled', 'use_ssl']:
                    db.set_config(key, value, 'boolean', f'是否{"启用" if value else "禁用"}相关功能')
                elif key in ['smtp_port', 'retry_times', 'retry_interval', 'timeout']:
                    db.set_config(key, value, 'integer', f'{key}配置值')
                else:
                    db.set_config(key, value, 'string', f'{key}配置值')
            
            print(f"配置迁移完成，共迁移 {len(json_config)} 项配置")
            
            # 备份原JSON文件
            backup_path = json_config_path + '.backup'
            os.rename(json_config_path, backup_path)
            print(f"原JSON配置文件已备份到: {backup_path}")
            
        except Exception as e:
            print(f"配置迁移失败: {e}")
    
    # 初始化默认配置和模板
    db.init_default_config()
    db.init_default_templates()
    
    print("数据库初始化完成")

if __name__ == "__main__":
    migrate_json_to_db()