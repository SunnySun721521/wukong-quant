#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单PDF导出测试
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("开始测试...")
print(f"Python版本: {sys.version}")

# 测试导入
print("\n测试导入reportlab...")
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO
    print("✅ reportlab导入成功")
except Exception as e:
    print(f"❌ reportlab导入失败: {e}")
    sys.exit(1)

# 测试创建PDF
print("\n测试创建PDF...")
try:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph("Test", styles['Normal'])]
    doc.build(story)
    print(f"✅ PDF创建成功，大小: {len(buffer.getvalue())} bytes")
except Exception as e:
    print(f"❌ PDF创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试导入app
print("\n测试导入app...")
try:
    from app import app, _execute_pdf_export
    print("✅ app导入成功")
except Exception as e:
    print(f"❌ app导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试PDF导出函数
print("\n测试_execute_pdf_export函数...")
try:
    with app.app_context():
        result = _execute_pdf_export()
        if result:
            print(f"✅ PDF导出成功: {result}")
            if os.path.exists(result):
                print(f"✅ 文件存在，大小: {os.path.getsize(result)} bytes")
            else:
                print(f"❌ 文件不存在: {result}")
        else:
            print("❌ PDF导出返回None")
except Exception as e:
    print(f"❌ PDF导出失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成")
