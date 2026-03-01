#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细PDF导出测试脚本
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 导入必要的模块
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet

print("=" * 60)
print("详细PDF导出测试")
print("=" * 60)

# 测试1: 检查reportlab是否正常工作
print("\n测试1: 检查reportlab...")
try:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    doc.build(story)
    print("✅ reportlab基本功能正常")
except Exception as e:
    print(f"❌ reportlab错误: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 检查字体配置
print("\n测试2: 检查字体配置...")
try:
    from app import CHINESE_FONT
    print(f"中文字体配置: {CHINESE_FONT}")
except Exception as e:
    print(f"❌ 字体配置错误: {e}")

# 测试3: 检查数据目录
print("\n测试3: 检查数据目录...")
data_dir = os.path.join(os.path.dirname(__file__), 'backend', 'data')
scheduled_pdfs_dir = os.path.join(data_dir, 'scheduled_pdfs')
print(f"数据目录: {data_dir}")
print(f"  存在: {os.path.exists(data_dir)}")
print(f"PDF目录: {scheduled_pdfs_dir}")
print(f"  存在: {os.path.exists(scheduled_pdfs_dir)}")

# 测试4: 尝试创建PDF目录
print("\n测试4: 创建PDF目录...")
try:
    os.makedirs(scheduled_pdfs_dir, exist_ok=True)
    print(f"✅ PDF目录创建成功")
except Exception as e:
    print(f"❌ 创建目录失败: {e}")

# 测试5: 尝试写入测试文件
print("\n测试5: 测试文件写入...")
test_file = os.path.join(scheduled_pdfs_dir, "test.txt")
try:
    with open(test_file, 'w') as f:
        f.write("test")
    print(f"✅ 测试文件写入成功: {test_file}")
    os.remove(test_file)
    print(f"✅ 测试文件删除成功")
except Exception as e:
    print(f"❌ 文件操作失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
