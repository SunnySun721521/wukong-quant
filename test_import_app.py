#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, r'D:\trae\备份悟空52224\backend')

print("开始导入app模块...")

try:
    from app import app, pdf_scheduler, _execute_pdf_export, _send_email_notification
    print("✅ 导入成功")
    
    print(f"\npdf_scheduler: {pdf_scheduler}")
    print(f"pdf_export_callback: {pdf_scheduler.pdf_export_callback}")
    print(f"email_send_callback: {pdf_scheduler.email_send_callback}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
