#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render专用配置 - 覆盖默认邮箱配置
不影响本地程序运行
"""

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

def patch_email_config_manager():
    """修补 EmailConfigManager 以使用 Render 默认配置"""
    try:
        import os
        if not (os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_NAME')):
            return False
        
        print("[Render] 修补 EmailConfigManager...")
        
        from email_config_db import EmailConfigManager
        
        original_init_default = EmailConfigManager.init_default_config
        
        def patched_init_default(self):
            """修补后的初始化默认配置"""
            original_init_default(self)
            
            render_config = get_render_default_config()
            
            for key, value in render_config.items():
                try:
                    current = self.get_config(key)
                    print(f"[Render] 检查配置 {key}: 当前值={current}")
                    if current is None:
                        self.set_config(key, str(value))
                        print(f"[Render] 设置默认配置: {key} = {value}")
                    elif key == 'enabled' and current != 'true':
                        self.set_config(key, 'true')
                        print(f"[Render] 强制启用: {key} = true")
                    elif key in ['sender_email', 'sender_auth_code', 'recipients']:
                        if not current or current == '':
                            self.set_config(key, str(value))
                            print(f"[Render] 补充空值配置: {key} = {value}")
                except Exception as e:
                    print(f"[Render] 设置配置失败 {key}: {e}")
            
            all_config = self.get_all_config()
            print(f"[Render] 最终配置: {all_config}")
            print("[Render] EmailConfigManager 修补完成")
        
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
