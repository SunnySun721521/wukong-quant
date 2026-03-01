#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试回调函数是否被正确设置
"""

import sys
import os
sys.path.insert(0, r'D:\trae\备份悟空52224\backend')

# 设置环境变量
os.environ['FLASK_APP'] = 'app.py'

from app import app, pdf_scheduler, _execute_pdf_export, _send_email_notification

def test_callbacks():
    print("=" * 60)
    print("测试回调函数设置")
    print("=" * 60)
    
    print(f"\nPDF导出回调函数: {pdf_scheduler.pdf_export_callback}")
    print(f"邮件发送回调函数: {pdf_scheduler.email_send_callback}")
    
    print(f"\n_execute_pdf_export 函数: {_execute_pdf_export}")
    print(f"_send_email_notification 函数: {_send_email_notification}")
    
    # 检查回调函数是否匹配
    if pdf_scheduler.pdf_export_callback == _execute_pdf_export:
        print("\n✅ PDF导出回调函数已正确设置")
    else:
        print("\n❌ PDF导出回调函数未正确设置")
    
    if pdf_scheduler.email_send_callback == _send_email_notification:
        print("✅ 邮件发送回调函数已正确设置")
    else:
        print("❌ 邮件发送回调函数未正确设置")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_callbacks()
