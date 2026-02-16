#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库中的收件人记录"""

import sqlite3
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'data', 'email_config.db')

print(f"数据库路径: {db_path}")
print(f"数据库是否存在: {os.path.exists(db_path)}")

if not os.path.exists(db_path):
    print("数据库文件不存在！")
    exit(1)

try:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n数据库中的表: {[table[0] for table in tables]}")
        
        # 检查email_recipients表
        if 'email_recipients' in [table[0] for table in tables]:
            cursor.execute('SELECT * FROM email_recipients ORDER BY email_address')
            recipients = cursor.fetchall()
            
            print(f"\n收件人记录数量: {len(recipients)}")
            
            if recipients:
                print("\n收件人列表:")
                for recipient in recipients:
                    print(f"  ID: {recipient['id']}")
                    print(f"  邮箱: {recipient['email_address']}")
                    print(f"  姓名: {recipient['name']}")
                    print(f"  描述: {recipient['description']}")
                    print(f"  是否激活: {recipient['is_active']}")
                    print(f"  创建时间: {recipient['created_at']}")
                    print("  ---")
            else:
                print("\n没有收件人记录！")
        else:
            print("\nemail_recipients 表不存在！")
            
        # 检查email_config表
        if 'email_config' in [table[0] for table in tables]:
            cursor.execute('SELECT * FROM email_config')
            configs = cursor.fetchall()
            
            print(f"\n邮件配置记录数量: {len(configs)}")
            
            if configs:
                print("\n邮件配置:")
                for config in configs:
                    print(f"  {config['config_key']}: {config['config_value']}")
        else:
            print("\nemail_config 表不存在！")
            
except Exception as e:
    print(f"检查数据库失败: {e}")
    import traceback
    traceback.print_exc()
