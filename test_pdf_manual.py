#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动测试PDF导出功能
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app

def test_pdf_export():
    """测试PDF导出API"""
    print("=" * 60)
    print("手动测试PDF导出")
    print("=" * 60)
    
    with app.test_client() as client:
        print("\n发送请求到 /api/plan/export-pdf...")
        try:
            response = client.get('/api/plan/export-pdf?available_cash=187500.00&original_cash=200000.00')
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ PDF导出成功")
                print(f"Content-Type: {response.content_type}")
                print(f"Content-Length: {len(response.data)} bytes")
            else:
                print(f"❌ PDF导出失败")
                try:
                    error_data = response.get_json()
                    print(f"错误信息: {error_data}")
                except:
                    print(f"响应内容: {response.data[:200]}")
                    
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_pdf_export()
