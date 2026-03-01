#!/usr/bin/env python3
import sqlite3

db_path = r'D:\trae\备份悟空52224\backend\data\email_config.db'

print("=" * 60)
print("修复收件人启用状态")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 更新所有收件人为启用状态
    cursor.execute("UPDATE email_recipients SET is_active = 1")
    conn.commit()
    
    # 验证更新
    cursor.execute("SELECT * FROM email_recipients")
    recipients = cursor.fetchall()
    print(f"✅ 已更新 {len(recipients)} 个收件人为启用状态")
    for recipient in recipients:
        print(f"  ID: {recipient[0]}, 邮箱: {recipient[1]}, 名称: {recipient[2]}, 启用: {recipient[3]}")
    
    conn.close()
    print("\n✅ 修复完成")
except Exception as e:
    print(f"❌ 修复失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
