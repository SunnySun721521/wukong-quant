#!/usr/bin/env python3
import sqlite3

db_path = r'D:\trae\备份悟空52224\backend\data\email_config.db'

print("=" * 60)
print("检查is_active字段值")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询is_active字段
    cursor.execute("SELECT id, email_address, is_active, typeof(is_active) FROM email_recipients")
    recipients = cursor.fetchall()
    print(f"收件人记录:")
    for recipient in recipients:
        print(f"  ID: {recipient[0]}, 邮箱: {recipient[1]}, is_active: {recipient[2]}, 类型: {recipient[3]}")
    
    # 尝试重新更新
    print("\n更新is_active为1...")
    cursor.execute("UPDATE email_recipients SET is_active = 1 WHERE is_active IS NULL OR is_active = 0")
    conn.commit()
    print(f"更新了 {cursor.rowcount} 行")
    
    # 再次查询
    cursor.execute("SELECT id, email_address, is_active, typeof(is_active) FROM email_recipients")
    recipients = cursor.fetchall()
    print(f"\n更新后:")
    for recipient in recipients:
        print(f"  ID: {recipient[0]}, 邮箱: {recipient[1]}, is_active: {recipient[2]}, 类型: {recipient[3]}")
    
    conn.close()
except Exception as e:
    print(f"❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
