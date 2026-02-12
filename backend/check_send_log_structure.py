import sqlite3

db_path = r'D:\trae\备份悟空52220\backend\data\email_config.db'

print("=" * 50)
print("检查email_send_log表结构")
print("=" * 50)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取表结构
    cursor.execute('PRAGMA table_info(email_send_log)')
    columns = cursor.fetchall()
    
    print("\n表结构:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 查询所有记录
    cursor.execute('SELECT * FROM email_send_log')
    logs = cursor.fetchall()
    print(f"\n记录数: {len(logs)}")
    
    if logs:
        print("\n所有记录:")
        for log in logs:
            print(f"  {log}")
    
    conn.close()
    
except Exception as e:
    print(f"检查失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("检查完成")
print("=" * 50)