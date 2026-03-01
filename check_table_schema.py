#!/usr/bin/env python3
import sqlite3

db_path = r'D:\trae\备份悟空52224\backend\data\email_config.db'

print("=" * 60)
print("检查表结构")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查email_recipients表结构
    cursor.execute("PRAGMA table_info(email_recipients)")
    columns = cursor.fetchall()
    print("email_recipients 表结构:")
    for col in columns:
        print(f"  {col}")
    
    conn.close()
except Exception as e:
    print(f"❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
