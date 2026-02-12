import sqlite3
import json

# 修复邮件配置中的收件人设置
conn = sqlite3.connect('data/email_config.db')
cursor = conn.cursor()

# 更新收件人配置
cursor.execute('UPDATE email_config SET config_value = ? WHERE config_key = "recipients"', (json.dumps(["lib@tcscd.com"]),))

# 提交更改
conn.commit()

# 验证更新
cursor.execute('SELECT config_key, config_value FROM email_config WHERE config_key="recipients"')
result = cursor.fetchone()
print(f"更新后的收件人配置: {result}")

conn.close()