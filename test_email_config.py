#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件配置测试脚本
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from email_config_manager import EmailConfigManager

def test_email_config():
    """测试邮件配置"""
    print("=" * 60)
    print("邮件配置测试")
    print("=" * 60)
    
    # 创建配置管理器实例
    config_manager = EmailConfigManager()
    
    # 获取当前配置
    config = config_manager.get_config()
    
    print("\n当前邮件配置:")
    print(f"  启用状态: {config.get('enabled', False)}")
    print(f"  发件邮箱: {config.get('sender_email', '未设置')}")
    print(f"  授权码: {'已设置' if config.get('sender_auth_code') else '未设置'}")
    print(f"  SMTP服务器: {config.get('smtp_server', 'smtp.qq.com')}")
    print(f"  SMTP端口: {config.get('smtp_port', 465)}")
    print(f"  使用SSL: {config.get('use_ssl', True)}")
    print(f"  收件人列表: {config.get('recipients', [])}")
    
    # 验证配置
    print("\n配置验证:")
    is_valid, error_msg = config_manager.validate_config()
    if is_valid:
        print("  ✅ 配置验证通过")
        if error_msg:
            print(f"  ℹ️ 提示: {error_msg}")
    else:
        print(f"  ❌ 配置验证失败: {error_msg}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_email_config()
