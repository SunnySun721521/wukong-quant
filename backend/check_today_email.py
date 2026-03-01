import sqlite3

db_path = r'D:\trae\备份悟空52220\backend\data\email_config.db'

print("=" * 50)
print("检查今天的邮件发送记录")
print("=" * 50)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询今天的邮件发送记录
    cursor.execute("SELECT * FROM email_send_log WHERE created_at >= '2026-02-10' ORDER BY created_at DESC")
    logs = cursor.fetchall()
    
    print(f"\n今天(2026-02-10)的邮件发送记录: {len(logs)}条")
    
    if logs:
        for log in logs:
            print(f"\n记录ID: {log[0]}")
            print(f"  PDF文件: {log[3]}")
            print(f"  状态: {log[4]}")
            print(f"  收件人: {log[5]}")
            print(f"  错误信息: {log[6]}")
            print(f"  重试次数: {log[7]}")
            print(f"  创建时间: {log[8]}")
    else:
        print("  没有今天的邮件发送记录")
    
    conn.close()
    
except Exception as e:
    print(f"检查失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("检查完成")
print("=" * 50)