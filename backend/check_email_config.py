import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'email_config.db')

print("=" * 50)
print("检查邮件配置")
print("=" * 50)
print(f"数据库路径: {db_path}")

if not os.path.exists(db_path):
    print(f"错误: 数据库文件不存在")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. 检查邮件配置
print("\n1. 邮件配置:")
cursor.execute('SELECT config_key, config_value, config_type FROM email_config')
configs = cursor.fetchall()
for key, value, config_type in configs:
    if key in ['sender_auth_code', 'sender_email']:
        print(f"  {key}: {'*' * 10} (已隐藏)")
    else:
        print(f"  {key}: {value}")

# 2. 检查收件人列表
print("\n2. 收件人列表:")
cursor.execute('SELECT id, email_address, name, description, is_active FROM email_recipients')
recipients = cursor.fetchall()
print(f"  总数: {len(recipients)}")
for rec in recipients:
    print(f"  ID={rec[0]}, 邮箱={rec[1]}, 姓名={rec[2]}, 描述={rec[3]}, 激活={rec[4]}")

# 3. 检查SMTP配置
print("\n3. SMTP配置:")
cursor.execute("SELECT config_value FROM email_config WHERE config_key = 'smtp_server'")
smtp_server = cursor.fetchone()
if smtp_server:
    print(f"  SMTP服务器: {smtp_server[0]}")

cursor.execute("SELECT config_value FROM email_config WHERE config_key = 'smtp_port'")
smtp_port = cursor.fetchone()
if smtp_port:
    print(f"  SMTP端口: {smtp_port[0]}")

cursor.execute("SELECT config_value FROM email_config WHERE config_key = 'use_ssl'")
use_ssl = cursor.fetchone()
if use_ssl:
    print(f"  使用SSL: {use_ssl[0]}")

cursor.execute("SELECT config_value FROM email_config WHERE config_key = 'timeout'")
timeout = cursor.fetchone()
if timeout:
    print(f"  超时时间: {timeout[0]}秒")

conn.close()

print("\n" + "=" * 50)
print("检查完成")
print("=" * 50)