import sqlite3

db_path = r'D:\trae\备份悟空52220\backend\data\email_config.db'

print("=" * 50)
print("检查数据库表结构")
print("=" * 50)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查看所有表
    print("\n数据库中的所有表:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table[0]}")
    
    # 检查email_logs表是否存在
    if 'email_logs' in [t[0] for t in tables]:
        print("\nemail_logs表存在")
        cursor.execute('SELECT COUNT(*) FROM email_logs')
        count = cursor.fetchone()[0]
        print(f"  记录数: {count}")
    else:
        print("\nemail_logs表不存在")
    
    conn.close()
    
except Exception as e:
    print(f"检查失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("检查完成")
print("=" * 50)