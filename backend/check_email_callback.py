import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
import sqlite3

print("=" * 50)
print("检查邮件配置和回调函数")
print("=" * 50)

# 1. 检查邮件配置
print("\n1. 检查邮件配置:")
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'email_config.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT config_key, config_value FROM email_config')
configs = cursor.fetchall()
for key, value in configs:
    if key == 'enabled':
        print(f"  {key}: {value}")
    elif key == 'sender_email':
        print(f"  {key}: {value}")
    elif key == 'recipients':
        print(f"  {key}: {value}")

# 2. 检查收件人
print("\n2. 检查收件人:")
cursor.execute('SELECT id, email_address, is_active FROM email_recipients')
recipients = cursor.fetchall()
print(f"  总数: {len(recipients)}")
for rec in recipients:
    print(f"  ID={rec[0]}, 邮箱={rec[1]}, 激活={rec[2]}")

conn.close()

# 3. 检查回调函数
print("\n3. 检查PDF调度器回调函数:")
print(f"  PDF导出回调: {app.pdf_scheduler.pdf_export_callback is not None}")
print(f"  邮件发送回调: {app.pdf_scheduler.email_send_callback is not None}")
print(f"  数据更新回调数: {len(app.pdf_scheduler.data_update_callbacks)}")

# 4. 测试邮件发送
print("\n4. 测试邮件发送:")
with app.app.test_client() as client:
    response = client.post('/api/email/test')
    data = response.get_json()
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {data}")

print("\n" + "=" * 50)
print("检查完成")
print("=" * 50)