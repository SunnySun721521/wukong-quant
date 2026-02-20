#!/usr/bin/env python3
import sqlite3
import json

db_path = r'D:\trae\备份悟空52224\backend\data\email_config.db'

print("=" * 60)
print("检查收件人列表")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查email_recipients表
    cursor.execute("SELECT * FROM email_recipients")
    recipients = cursor.fetchall()
    print(f"收件人记录数: {len(recipients)}")
    for recipient in recipients:
        print(f"  ID: {recipient[0]}, 邮箱: {recipient[1]}, 名称: {recipient[2]}, 启用: {recipient[3]}")
    
    # 从配置表中获取recipients
    cursor.execute("SELECT config_value FROM email_config WHERE config_key = 'recipients'")
    result = cursor.fetchone()
    if result:
        recipients_json = result[0]
        recipients_list = json.loads(recipients_json)
        print(f"\n配置中的收件人列表: {recipients_list}")
    
    conn.close()
except Exception as e:
    print(f"❌ 读取数据库失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
