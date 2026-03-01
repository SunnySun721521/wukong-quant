#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def check_pdf_files():
    """检查PDF文件"""
    pdf_dir = r"d:\trae\备份悟空52220\backend\scheduled_pdfs"
    
    print(f"检查目录: {pdf_dir}")
    print(f"目录存在: {os.path.exists(pdf_dir)}")
    
    if os.path.exists(pdf_dir):
        try:
            files = os.listdir(pdf_dir)
            print(f"\n目录中的文件 ({len(files)} 个):")
            
            if not files:
                print("  目录为空")
            else:
                for i, filename in enumerate(files, 1):
                    filepath = os.path.join(pdf_dir, filename)
                    if os.path.isfile(filepath):
                        size = os.path.getsize(filepath)
                        print(f"  {i}. {filename} ({size:,} 字节)")
                        
                        # 检查是否是测试邮件PDF
                        if "测试邮件" in filename:
                            print(f"     → 这是测试邮件PDF")
                            
                            # 读取文件内容检查字体
                            try:
                                with open(filepath, 'rb') as f:
                                    content = f.read()
                                    
                                if b'msyh' in content:
                                    print(f"     ✓ 使用了中文字体 (Microsoft YaHei)")
                                elif b'Helvetica' in content:
                                    print(f"     ✗ 使用了默认字体 (Helvetica) - 可能乱码")
                                else:
                                    print(f"     ? 未检测到明确的字体信息")
                            except Exception as e:
                                print(f"     ✗ 读取文件失败: {e}")
        except Exception as e:
            print(f"列出文件失败: {e}")
    else:
        print("目录不存在")

if __name__ == "__main__":
    check_pdf_files()
