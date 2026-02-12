import sqlite3

db_path = r'D:\trae\备份悟空52220\backend\data\email_config.db'

print("=" * 50)
print("检查邮件发送日志")
print("=" * 50)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查email_send_log表
    print("\nemail_send_log表记录:")
    cursor.execute('SELECT * FROM email_send_log ORDER BY timestamp DESC LIMIT 10')
    logs = cursor.fetchall()
    
    # 获取列名
    cursor.execute('PRAGMA table_info(email_send_log)')
    columns = [col[1] for col in cursor.fetchall()]
    print(f"  列名: {columns}")
    print(f"  记录数: {len(logs)}")
    
    if logs:
        print("\n  最近10条记录:")
        for log in logs:
            print(f"  {log}")
    else:
        print("  没有记录")
    
    conn.close()
    
except Exception as e:
    print(f"检查失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("检查完成")
print("=" * 50)