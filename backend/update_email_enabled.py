import sqlite3
import os

# 更新邮件配置中的enabled状态为true
conn = sqlite3.connect('data/email_config.db')
cursor = conn.cursor()

# 检查是否存在enabled配置
cursor.execute('SELECT config_value FROM email_config WHERE config_key="enabled"')
result = cursor.fetchone()

if result:
    # 更新现有配置
    cursor.execute('UPDATE email_config SET config_value = "true" WHERE config_key = "enabled"')
    print("更新现有enabled配置为true")
else:
    # 插入新配置
    cursor.execute('INSERT INTO email_config (config_key, config_value, config_type, description) VALUES ("enabled", "true", "boolean", "是否启用邮件发送")')
    print("插入新的enabled配置为true")

# 提交更改
conn.commit()

# 验证更新
cursor.execute('SELECT config_key, config_value FROM email_config WHERE config_key="enabled"')
result = cursor.fetchone()
print(f"更新后的enabled配置: {result}")

conn.close()