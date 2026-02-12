#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
from datetime import datetime

BASE_URL = "http://127.0.0.1:5006"

def test_pdf_export():
    """测试PDF导出功能"""
    print("=" * 50)
    print("测试PDF导出功能")
    print("=" * 50)
    
    try:
        # 获取当前现金配置
        print("\n1. 获取当前现金配置...")
        response = requests.get(f"{BASE_URL}/api/config/available_cash", timeout=10)
        if response.status_code == 200:
            config = response.json()
            available_cash = config.get('available_cash', 187500.00)
            original_cash = config.get('original_cash', 200000.00)
            print(f"  可用现金: ¥{available_cash:,.2f}")
            print(f"  原始资金: ¥{original_cash:,.2f}")
        else:
            print(f"  获取配置失败，使用默认值")
            available_cash = 187500.00
            original_cash = 200000.00
        
        # 导出PDF
        print("\n2. 导出PDF...")
        export_url = f"{BASE_URL}/api/plan/export-pdf?available_cash={available_cash}&original_cash={original_cash}"
        print(f"  请求URL: {export_url}")
        
        response = requests.get(export_url, timeout=30)
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 保存PDF文件
            filename = f"测试PDF_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(os.path.dirname(__file__), filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"  ✓ PDF导出成功")
            print(f"  文件名: {filename}")
            print(f"  文件大小: {file_size:,} 字节")
            print(f"  保存路径: {filepath}")
            
            # 检查文件是否为有效的PDF
            if response.content.startswith(b'%PDF'):
                print(f"  ✓ 文件格式验证通过（PDF格式）")
            else:
                print(f"  ✗ 文件格式验证失败（非PDF格式）")
            
            return filepath
        else:
            print(f"  ✗ PDF导出失败")
            print(f"  错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_email_attachment():
    """测试邮件附件功能"""
    print("\n" + "=" * 50)
    print("测试邮件附件功能")
    print("=" * 50)
    
    try:
        # 获取当前邮件配置
        print("\n1. 获取当前邮件配置...")
        response = requests.get(f"{BASE_URL}/api/email/config", timeout=10)
        if response.status_code == 200:
            config = response.json()
            print(f"  发送邮箱: {config.get('sender_email')}")
            print(f"  接收人: {config.get('recipients')}")
            print(f"  功能状态: {'启用' if config.get('enabled') else '禁用'}")
        else:
            print(f"  获取配置失败: {response.text}")
            return
        
        # 检查是否有测试PDF文件
        print("\n2. 检查测试PDF文件...")
        test_files = [f for f in os.listdir(os.path.dirname(__file__)) if f.startswith('测试PDF_') and f.endswith('.pdf')]
        
        if test_files:
            latest_file = max(test_files)
            filepath = os.path.join(os.path.dirname(__file__), latest_file)
            print(f"  找到测试文件: {latest_file}")
            
            # 发送测试邮件
            print("\n3. 发送测试邮件...")
            test_data = {
                'recipients': config.get('recipients', [])
            }
            
            response = requests.post(f"{BASE_URL}/api/email/test", json=test_data, timeout=60)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ {result.get('message')}")
                print(f"  接收人: {result.get('recipients')}")
            else:
                result = response.json()
                print(f"  ✗ {result.get('error')}")
        else:
            print(f"  未找到测试PDF文件")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        # 测试PDF导出
        pdf_file = test_pdf_export()
        
        # 测试邮件附件
        if pdf_file:
            test_email_attachment()
        
        print("\n" + "=" * 50)
        print("测试完成")
        print("=" * 50)
        print("\n验证要点:")
        print("1. 打开导出的PDF文件，检查:")
        print("   - 市场状态: 牛市显示为红色，熊市显示为绿色")
        print("   - 持仓盈亏: 亏损显示为绿色，盈利显示为红色")
        print("2. 检查邮件附件:")
        print("   - 附件文件名应正确显示中文（不再乱码）")
        print("   - 附件内容应能正常打开")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
