#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def check_directory():
    """检查目录和文件"""
    pdf_dir = r"d:\trae\备份悟空52220\backend\scheduled_pdfs"
    
    print(f"检查目录: {pdf_dir}")
    print(f"目录存在: {os.path.exists(pdf_dir)}")
    
    if os.path.exists(pdf_dir):
        print(f"是目录: {os.path.isdir(pdf_dir)}")
        
        # 列出所有文件
        try:
            files = os.listdir(pdf_dir)
            print(f"\n目录中的文件 ({len(files)} 个):")
            for i, filename in enumerate(files, 1):
                filepath = os.path.join(pdf_dir, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    print(f"  {i}. {filename} ({size:,} 字节)")
                else:
                    print(f"  {i}. {filename} (目录)")
        except Exception as e:
            print(f"列出文件失败: {e}")
    else:
        print("目录不存在")

if __name__ == "__main__":
    check_directory()
