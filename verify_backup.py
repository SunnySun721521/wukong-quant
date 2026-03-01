#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import hashlib
from pathlib import Path

def calculate_file_hash(file_path):
    """计算文件的SHA256哈希值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_backup():
    """验证备份文件内容一致性"""
    
    source = r"D:\trae\备份悟空52220"
    dest = r"D:\trae\备份悟空52222"
    
    print("=" * 60)
    print("文件内容一致性验证（抽样检查）")
    print("=" * 60)
    print()
    
    test_files = [
        "backend/app.py",
        "web/plan.html",
        "web/settings.html",
        "strategy/data/stock_pool.json"
    ]
    
    all_match = True
    
    for file in test_files:
        src_file = os.path.join(source, file)
        dst_file = os.path.join(dest, file)
        
        if os.path.exists(src_file) and os.path.exists(dst_file):
            src_hash = calculate_file_hash(src_file)
            dst_hash = calculate_file_hash(dst_file)
            
            if src_hash == dst_hash:
                print(f"✅ {file} - 内容一致")
            else:
                print(f"❌ {file} - 内容不一致")
                all_match = False
        else:
            print(f"⚠️  {file} - 文件不存在")
            all_match = False
    
    print()
    if all_match:
        print("✅ 文件内容验证通过！")
    else:
        print("❌ 文件内容验证失败！")
    
    print("=" * 60)

if __name__ == "__main__":
    verify_backup()
