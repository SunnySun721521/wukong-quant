import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'email_config.db')

print("=" * 50)
print("检查数据库表结构")
print("=" * 50)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查看所有表
print("\n数据库中的所有表:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# 检查每个表的结构
for table in tables:
    table_name = table[0]
    print(f"\n{table_name} 表结构:")
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 查看记录数
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    print(f"  记录数: {count}")

conn.close()

print("\n" + "=" * 50)
print("检查完成")
print("=" * 50)