#!/usr/bin/env python3
import sqlite3
from datetime import datetime

db_path = r'D:\trae\备份悟空52224\backend\data\email_config.db'

print("=" * 60)
print("检查今天的邮件发送成功记录")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 查询今天的邮件发送日志（排除测试记录）
    cursor.execute("""
        SELECT * FROM email_send_log 
        WHERE created_at LIKE ? 
        AND pdf_file NOT LIKE '%test.pdf%'
        ORDER BY created_at DESC
    """, (f'{today}%',))
    logs = cursor.fetchall()
    
    print(f"\n今天({today})的邮件发送记录:")
    if logs:
        for log in logs:
            print(f"\n  ID: {log['id']}")
            print(f"  PDF文件: {log['pdf_file']}")
            print(f"  状态: {log['status']}")
            print(f"  收件人: {log['recipients']}")
            print(f"  发送时间: {log['created_at']}")
    else:
        print("  今天没有邮件发送记录（不包括测试记录）")
    
    # 查询所有今天的记录
    print(f"\n今天所有邮件记录:")
    cursor.execute("SELECT id, status, pdf_file, created_at FROM email_send_log WHERE created_at LIKE ? ORDER BY created_at DESC", (f'{today}%',))
    all_logs = cursor.fetchall()
    for log in all_logs:
        pdf_name = log['pdf_file'].split('\\')[-1] if '\\' in log['pdf_file'] else log['pdf_file']
        print(f"  ID: {log['id']}, 状态: {log['status']}, 文件: {pdf_name}, 时间: {log['created_at']}")
    
    conn.close()
except Exception as e:
    print(f"❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
