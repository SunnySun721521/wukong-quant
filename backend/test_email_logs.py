#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email_config_db import EmailConfigDB

def test_email_logs():
    """测试邮件日志"""
    try:
        db = EmailConfigDB()
        logs = db.get_email_logs(5)
        print('最近5条邮件发送日志:')
        for log in logs:
            print(f"时间: {log['timestamp']}, 状态: {log['status']}, 收件人: {len(log['recipients'])}")
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_email_logs()