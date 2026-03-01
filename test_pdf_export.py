#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF导出功能
"""

import sys
import os
sys.path.insert(0, r'D:\trae\备份悟空52224\backend')

# 设置环境变量
os.environ['FLASK_APP'] = 'app.py'

from app import app, _execute_pdf_export

def test_pdf_export():
    print("=" * 60)
    print("测试PDF导出功能")
    print("=" * 60)
    
    with app.app_context():
        print("\n开始执行PDF导出...")
        try:
            result = _execute_pdf_export()
            if result:
                print(f"\n✅ PDF导出成功: {result}")
                # 检查文件是否存在
                if os.path.exists(result):
                    file_size = os.path.getsize(result)
                    print(f"✅ 文件存在，大小: {file_size} bytes")
                else:
                    print(f"❌ 文件不存在: {result}")
            else:
                print("\n❌ PDF导出失败，返回None")
        except Exception as e:
            print(f"\n❌ PDF导出异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_pdf_export()
