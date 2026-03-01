import sqlite3

db_path = r'D:\trae\备份悟空52220\backend\data\email_config.db'

print("=" * 50)
print("检查邮件配置和收件人")
print("=" * 50)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 检查邮件配置
    print("\n1. 邮件配置:")
    cursor.execute('SELECT config_key, config_value FROM email_config')
    configs = cursor.fetchall()
    for key, value in configs:
        print(f"  {key}: {value}")
    
    # 2. 检查收件人列表
    print("\n2. 收件人列表:")
    cursor.execute('SELECT id, email_address, name, description, is_active FROM email_recipients')
    recipients = cursor.fetchall()
    print(f"  总数: {len(recipients)}")
    for rec in recipients:
        print(f"  ID={rec[0]}, 邮箱={rec[1]}, 姓名={rec[2]}, 描述={rec[3]}, 激活={rec[4]}")
    
    # 3. 检查邮件发送日志
    print("\n3. 邮件发送日志:")
    cursor.execute('SELECT * FROM email_logs ORDER BY timestamp DESC LIMIT 10')
    logs = cursor.fetchall()
    print(f"  最近10条记录:")
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