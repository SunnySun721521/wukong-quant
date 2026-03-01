#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的定时任务执行流程
"""

import sys
import os
sys.path.insert(0, r'D:\trae\备份悟空52224\backend')

# 设置环境变量
os.environ['FLASK_APP'] = 'app.py'

from app import app, pdf_scheduler, _execute_pdf_export, _send_email_notification

def test_scheduler_callbacks():
    print("=" * 60)
    print("测试调度器回调函数")
    print("=" * 60)
    
    print(f"\nPDF导出回调函数: {pdf_scheduler.pdf_export_callback}")
    print(f"邮件发送回调函数: {pdf_scheduler.email_send_callback}")
    
    with app.app_context():
        print("\n测试PDF导出...")
        try:
            pdf_path = _execute_pdf_export()
            if pdf_path:
                print(f"✅ PDF导出成功: {pdf_path}")
                
                # 检查文件是否存在
                if os.path.exists(pdf_path):
                    file_size = os.path.getsize(pdf_path)
                    print(f"✅ 文件存在，大小: {file_size} bytes")
                    
                    # 测试邮件发送
                    print("\n测试邮件发送...")
                    try:
                        _send_email_notification(pdf_path)
                        print("✅ 邮件发送回调执行完成")
                    except Exception as e:
                        print(f"❌ 邮件发送失败: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"❌ PDF文件不存在: {pdf_path}")
            else:
                print("❌ PDF导出返回None")
        except Exception as e:
            print(f"❌ PDF导出异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_scheduler_callbacks()
