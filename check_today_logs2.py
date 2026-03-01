#!/usr/bin/env python3
import sqlite3
from datetime import datetime

db_path = r'D:\trae\备份悟空52224\backend\data\email_config.db'

print("=" * 60)
print("检查今天的邮件发送日志")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"今天的日期: {today}")
    
    # 查询今天的邮件发送日志
    cursor.execute("SELECT * FROM email_send_log WHERE created_at LIKE ? ORDER BY created_at DESC", (f'{today}%',))
    logs = cursor.fetchall()
    
    print(f"\n今天({today})的邮件发送日志:")
    if logs:
        for log in logs:
            print(f"\n  ID: {log['id']}")
            print(f"  任务ID: {log['task_id']}")
            print(f"  PDF文件: {log['pdf_file']}")
            print(f"  状态: {log['status']}")
            print(f"  收件人: {log['recipients']}")
            print(f"  错误信息: {log['error_message']}")
            print(f"  重试次数: {log['retry_count']}")
            print(f"  创建时间: {log['created_at']}")
    else:
        print("  ❌ 今天没有邮件发送记录")
    
    conn.close()
except Exception as e:
    print(f"❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
