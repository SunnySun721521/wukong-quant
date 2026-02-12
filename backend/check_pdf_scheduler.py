import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
import sqlite3

print("=" * 50)
print("检查PDF调度器和邮件发送状态")
print("=" * 50)

# 1. 检查PDF调度器状态
print("\n1. PDF调度器状态:")
print(f"  运行中: {app.pdf_scheduler.is_running()}")
print(f"  定时任务: {app.pdf_scheduler.get_scheduled_times()}")
print(f"  PDF导出回调: {app.pdf_scheduler.pdf_export_callback is not None}")
print(f"  邮件发送回调: {app.pdf_scheduler.email_send_callback is not None}")

# 2. 检查邮件配置
print("\n2. 邮件配置:")
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'email_config.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT config_key, config_value FROM email_config WHERE config_key IN ('enabled', 'sender_email', 'recipients')")
configs = cursor.fetchall()
for key, value in configs:
    print(f"  {key}: {value}")

# 3. 检查收件人
print("\n3. 收件人:")
cursor.execute('SELECT id, email_address, is_active FROM email_recipients')
recipients = cursor.fetchall()
print(f"  总数: {len(recipients)}")
for rec in recipients:
    print(f"  ID={rec[0]}, 邮箱={rec[1]}, 激活={rec[2]}")

# 4. 检查今天的PDF执行日志
print("\n4. 今天的PDF执行日志:")
cursor.execute("SELECT * FROM email_send_log WHERE created_at >= '2026-02-10' ORDER BY created_at DESC")
logs = cursor.fetchall()
print(f"  记录数: {len(logs)}")
if logs:
    for log in logs:
        print(f"  PDF: {os.path.basename(log[3])}, 状态: {log[4]}, 时间: {log[8]}")

conn.close()

# 5. 检查今天的PDF文件
print("\n5. 今天的PDF文件:")
pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scheduled_pdfs')
if os.path.exists(pdf_dir):
    import os
    from datetime import datetime
    today_pdfs = [f for f in os.listdir(pdf_dir) if f.startswith('每日操作计划_20260210')]
    print(f"  文件数: {len(today_pdfs)}")
    for pdf in today_pdfs:
        print(f"  {pdf}")
else:
    print("  PDF目录不存在")

print("\n" + "=" * 50)
print("检查完成")
print("=" * 50)