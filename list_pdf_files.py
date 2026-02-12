#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob

def list_pdf_files():
    """列出PDF文件"""
    pdf_dir = r"d:\trae\备份悟空52220\backend\scheduled_pdfs"
    
    # 列出所有PDF文件
    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    
    print(f"PDF目录: {pdf_dir}")
    print(f"找到 {len(pdf_files)} 个PDF文件\n")
    
    # 按修改时间排序
    pdf_files.sort(key=os.path.getmtime, reverse=True)
    
    for i, pdf_file in enumerate(pdf_files[:10], 1):
        basename = os.path.basename(pdf_file)
        file_size = os.path.getsize(pdf_file)
        mtime = os.path.getmtime(pdf_file)
        mtime_str = os.path.getmtime(pdf_file)
        
        print(f"{i}. {basename}")
        print(f"   大小: {file_size:,} 字节")
        print(f"   修改时间: {mtime_str}")
        print()

if __name__ == "__main__":
    list_pdf_files()
