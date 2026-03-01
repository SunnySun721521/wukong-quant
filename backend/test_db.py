#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email_config_db import EmailConfigDB

def test_database():
    """测试数据库功能"""
    try:
        # 创建数据库连接
        db = EmailConfigDB()
        print("数据库连接成功")
        
        # 获取所有配置
        config = db.get_all_config()
        print(f"配置项数量: {len(config)}")
        
        # 获取启用状态
        enabled = config.get("enabled", False)
        print(f"启用状态: {enabled}")
        
        # 获取发送邮箱
        sender_email = config.get("sender_email", "")
        print(f"发送邮箱: {sender_email}")
        
        # 获取收件人列表
        recipients = config.get("recipients", [])
        print(f"收件人数量: {len(recipients)}")
        
        # 获取所有模板
        templates = db.get_all_templates()
        print(f"模板数量: {len(templates)}")
        
        print("数据库测试完成")
        return True
    except Exception as e:
        print(f"数据库测试失败: {e}")
        return False

if __name__ == "__main__":
    test_database()