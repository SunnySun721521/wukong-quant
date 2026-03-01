#!/usr/bin/env python3
import sys
sys.path.insert(0, r'D:\trae\备份悟空52224\backend')

from email_config_db import EmailConfigDB
import uuid

print("=" * 60)
print("测试邮件日志记录功能")
print("=" * 60)

try:
    db = EmailConfigDB()
    
    # 测试记录成功日志
    log_id = str(uuid.uuid4())
    result = db.log_email_send(
        log_id=log_id,
        pdf_file=r'D:\trae\备份悟空52224\backend\scheduled_pdfs\test.pdf',
        status='success',
        recipients=[
            {'email': 'test1@example.com', 'status': 'success'},
            {'email': 'test2@example.com', 'status': 'success'}
        ]
    )
    
    if result:
        print("✅ 测试日志记录成功")
    else:
        print("❌ 测试日志记录失败")
    
    # 获取最近的日志
    logs = db.get_email_logs(limit=5)
    print(f"\n最近5条日志:")
    for log in logs:
        print(f"  ID: {log['id']}, 状态: {log['status']}, 时间: {log['created_at']}")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
