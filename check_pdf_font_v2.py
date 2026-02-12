#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob

def check_pdf_font():
    """检查PDF文件中是否使用了中文字体"""
    pdf_dir = r"d:\trae\备份悟空52220\backend\scheduled_pdfs"
    
    # 查找最新的测试邮件PDF
    pdf_files = glob.glob(os.path.join(pdf_dir, "测试邮件*.pdf"))
    
    if not pdf_files:
        print(f"未找到测试邮件PDF文件")
        return
    
    # 获取最新的文件
    latest_file = max(pdf_files, key=os.path.getmtime)
    print(f"检查文件: {os.path.basename(latest_file)}")
    print(f"文件路径: {latest_file}")
    
    with open(latest_file, 'rb') as f:
        content = f.read()
    
    # 检查是否包含中文字体名称
    if b'msyh' in content:
        print("\n✓ PDF文件使用了中文字体 (Microsoft YaHei)")
        print("  中文字符应该能正确显示")
    elif b'Helvetica' in content:
        print("\n✗ PDF文件使用的是默认字体 (Helvetica)")
        print("  中文字符可能显示为乱码")
    else:
        print("\n? 未检测到明确的字体信息")
        print("  请手动打开PDF文件检查中文显示")
    
    # 检查文件大小
    file_size = len(content)
    print(f"\n文件大小: {file_size:,} 字节")
    
    # 检查PDF版本
    if content.startswith(b'%PDF-'):
        print("✓ 文件格式正确 (PDF)")
    else:
        print("✗ 文件格式不正确")

if __name__ == "__main__":
    check_pdf_font()
