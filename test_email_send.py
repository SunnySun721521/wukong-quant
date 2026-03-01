#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试邮件发送功能
"""

import sys
import os
sys.path.insert(0, r'D:\trae\备份悟空52224\backend')

# 设置环境变量
os.environ['FLASK_APP'] = 'app.py'

from app import app
from email_config_manager import EmailConfigManager

def test_email_config():
    print("=" * 60)
    print("测试邮件配置")
    print("=" * 60)
    
    with app.app_context():
        config_manager = EmailConfigManager()
        config = config_manager.get_config()
        
        print(f"\n邮件配置:")
        print(f"  enabled: {config.get('enabled', False)}")
        print(f"  sender_email: {config.get('sender_email', '')}")
        print(f"  sender_auth_code: {'*' * len(config.get('sender_auth_code', ''))}")
        print(f"  recipients: {config.get('recipients', [])}")
        print(f"  smtp_server: {config.get('smtp_server', '')}")
        print(f"  smtp_port: {config.get('smtp_port', '')}")
        
        # 验证配置
        is_valid, error_msg = config_manager.validate_config()
        print(f"\n配置验证结果:")
        print(f"  是否有效: {is_valid}")
        if error_msg:
            print(f"  错误信息: {error_msg}")
    
    print("=" * 60)

if __name__ == '__main__':
    test_email_config()
