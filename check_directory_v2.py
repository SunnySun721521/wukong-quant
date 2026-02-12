#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def check_directory():
    """检查目录和文件"""
    # 尝试不同的路径格式
    paths = [
        r"d:\trae\备份悟空52220\backend\scheduled_pdfs",
        r"d:\trae\备份悟空52220\backend\scheduled_pdfs",
        os.path.join(r"d:\trae\备份悟空52220", "backend", "scheduled_pdfs"),
    ]
    
    for path in paths:
        print(f"\n检查路径: {path}")
        print(f"  存在: {os.path.exists(path)}")
        
        if os.path.exists(path):
            print(f"  是目录: {os.path.isdir(path)}")
            
            try:
                files = os.listdir(path)
                print(f"  文件数: {len(files)}")
                
                if files:
                    print(f"  文件列表:")
                    for i, filename in enumerate(files[:5], 1):
                        filepath = os.path.join(path, filename)
                        if os.path.isfile(filepath):
                            size = os.path.getsize(filepath)
                            print(f"    {i}. {filename} ({size:,} 字节)")
            except Exception as e:
                print(f"  列出文件失败: {e}")

if __name__ == "__main__":
    check_directory()
