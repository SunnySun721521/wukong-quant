#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5006"

def test_send_test_email():
    """测试发送测试邮件"""
    print("=" * 50)
    print("测试发送测试邮件")
    print("=" * 50)
    
    # 获取当前邮件配置
    print("\n1. 获取当前邮件配置...")
    try:
        response = requests.get(f"{BASE_URL}/api/email/config", timeout=10)
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            config = response.json()
            print(f"  发送邮箱: {config.get('sender_email')}")
            print(f"  接收人: {config.get('recipients')}")
            print(f"  功能状态: {'启用' if config.get('enabled') else '禁用'}")
        else:
            print(f"  获取配置失败: {response.text}")
            return
    except Exception as e:
        print(f"  获取配置异常: {e}")
        return
    
    # 发送测试邮件
    print("\n2. 发送测试邮件...")
    test_data = {
        'recipients': config.get('recipients', [])
    }
    
    print(f"  发送请求数据: {json.dumps(test_data, ensure_ascii=False)}")
    
    try:
        print("  正在发送请求...")
        response = requests.post(f"{BASE_URL}/api/email/test", json=test_data, timeout=120)
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ {result.get('message')}")
            print(f"  接收人: {result.get('recipients')}")
        else:
            result = response.json()
            print(f"  ✗ {result.get('error')}")
    except requests.exceptions.Timeout:
        print(f"  ✗ 请求超时")
    except Exception as e:
        print(f"  ✗ 请求异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        test_send_test_email()
        print("\n" + "=" * 50)
        print("测试完成")
        print("=" * 50)
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
