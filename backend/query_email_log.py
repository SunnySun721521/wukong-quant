import sqlite3

# 查询邮件发送日志
conn = sqlite3.connect('data/email_config.db')
cursor = conn.cursor()
cursor.execute('SELECT created_at, status, pdf_file FROM email_send_log ORDER BY created_at DESC LIMIT 3')
for row in cursor.fetchall():
    print(f'时间: {row[0]}, 状态: {row[1]}, 文件: {row[2]}')
conn.close()