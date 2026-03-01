#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render专用配置 - 覆盖默认邮箱配置
不影响本地程序运行
"""

import os
import sqlite3

def get_render_default_config():
    """获取Render默认配置"""
    return {
        'sender_email': '25285603@qq.com',
        'sender_auth_code': 'gyzieuggwgmfbhhh',
        'smtp_server': 'smtp.qq.com',
        'smtp_port': '465',
        'use_ssl': 'true',
        'timeout': '30',
        'retry_times': '3',
        'retry_interval': '5',
        'email_subject_template': '每日操作计划 - {date}',
        'email_body_template': 'simple',
        'recipients': '["lib@tcscd.com"]',
        'enabled': 'true'
    }

def get_data_dir():
    """获取数据目录路径"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def ensure_email_config_saved():
    """确保邮箱配置被保存到数据库"""
    try:
        if not (os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_NAME')):
            return False
        
        print("[Render] 确保邮箱配置保存...")
        
        db_path = os.path.join(get_data_dir(), 'email_config.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
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
        
        render_config = get_render_default_config()
        
        for key, value in render_config.items():
            cursor.execute("SELECT config_value FROM email_config WHERE config_key = ?", (key,))
            result = cursor.fetchone()
            
            if result is None:
                cursor.execute(
                    "INSERT INTO email_config (config_key, config_value, config_type) VALUES (?, ?, 'string')",
                    (key, value)
                )
                print(f"[Render] 插入配置: {key} = {value}")
            else:
                needs_update = False
                if key == 'enabled' and result[0] != 'true':
                    needs_update = True
                elif key in ['sender_email', 'sender_auth_code', 'recipients', 'smtp_server', 'smtp_port']:
                    if not result[0] or result[0] == '':
                        needs_update = True
                
                if needs_update:
                    cursor.execute(
                        "UPDATE email_config SET config_value = ?, updated_at = CURRENT_TIMESTAMP WHERE config_key = ?",
                        (value, key)
                    )
                    print(f"[Render] 更新配置: {key} = {value}")
        
        cursor.execute("SELECT config_key, config_value FROM email_config")
        all_config = cursor.fetchall()
        print(f"[Render] 最终配置: {all_config}")
        
        conn.commit()
        conn.close()
        print("[Render] 邮箱配置保存完成")
        return True
        
    except Exception as e:
        print(f"[Render] 保存邮箱配置失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def patch_email_config_manager():
    """修补 EmailConfigManager 以使用 Render 默认配置"""
    try:
        import os
        if not (os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_NAME')):
            return False
        
        print("[Render] 修补 EmailConfigManager...")
        
        ensure_email_config_saved()
        
        from email_config_db import EmailConfigManager
        
        original_init_default = EmailConfigManager.init_default_config
        
        def patched_init_default(self):
            """修补后的初始化默认配置"""
            original_init_default(self)
            ensure_email_config_saved()
        
        EmailConfigManager.init_default_config = patched_init_default
        print("[Render] EmailConfigManager 已修补")
        return True
        
    except Exception as e:
        print(f"[Render] 修补失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def apply_render_patches():
    """应用所有 Render 修补"""
    import os
    if not (os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_NAME')):
        return
    
    print("[Render] 正在应用修补...")
    patch_email_config_manager()
