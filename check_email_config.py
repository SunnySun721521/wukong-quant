#!/usr/bin/env python3
import sqlite3
import os

db_path = r'D:\trae\备份悟空52224\backend\data\email_config.db'

print("=" * 60)
print("检查邮件配置数据库")
print("=" * 60)

if not os.path.exists(db_path):
    print(f"❌ 数据库文件不存在: {db_path}")
else:
    print(f"✅ 数据库文件存在: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n数据库表: {[t[0] for t in tables]}")
        
        # 检查email_config表
        if 'email_config' in [t[0] for t in tables]:
            cursor.execute("SELECT * FROM email_config")
            configs = cursor.fetchall()
            print(f"\n邮件配置记录数: {len(configs)}")
            for config in configs:
                print(f"  {config}")
        
        # 检查email_templates表
        if 'email_templates' in [t[0] for t in tables]:
            cursor.execute("SELECT * FROM email_templates")
            templates = cursor.fetchall()
            print(f"\n邮件模板记录数: {len(templates)}")
            for template in templates:
                print(f"  {template}")
        
        # 检查recipients表
        if 'recipients' in [t[0] for t in tables]:
            cursor.execute("SELECT * FROM recipients")
            recipients = cursor.fetchall()
            print(f"\n收件人记录数: {len(recipients)}")
            for recipient in recipients:
                print(f"  {recipient}")
        
        conn.close()
    except Exception as e:
        print(f"❌ 读取数据库失败: {e}")
        import traceback
        traceback.print_exc()

print("=" * 60)
