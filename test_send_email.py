#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

BASE_URL = "http://127.0.0.1:5006"

def test_send_test_email():
    """测试发送测试邮件"""
    print("=" * 50)
    print("测试发送测试邮件")
    print("=" * 50)
    
    # 获取当前邮件配置
    print("\n1. 获取当前邮件配置...")
    response = requests.get(f"{BASE_URL}/api/email/config")
    if response.status_code == 200:
        config = response.json()
        print(f"  发送邮箱: {config.get('sender_email')}")
        print(f"  接收人: {config.get('recipients')}")
        print(f"  功能状态: {'启用' if config.get('enabled') else '禁用'}")
    else:
        print(f"  获取配置失败: {response.text}")
        return
    
    # 发送测试邮件
    print("\n2. 发送测试邮件...")
    test_data = {
        'recipients': config.get('recipients', [])
    }
    
    response = requests.post(f"{BASE_URL}/api/email/test", json=test_data)
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✓ {result.get('message')}")
        print(f"  接收人: {result.get('recipients')}")
    else:
        result = response.json()
        print(f"  ✗ {result.get('error')}")
    
    # 检查邮件发送日志
    print("\n3. 检查邮件发送日志...")
    response = requests.get(f"{BASE_URL}/api/email/logs")
    if response.status_code == 200:
        logs = response.json()
        print(f"  日志数量: {len(logs.get('logs', []))}")
        if logs.get('logs'):
            latest_log = logs['logs'][0]
            print(f"  最新日志状态: {latest_log.get('status')}")
            print(f"  PDF文件: {latest_log.get('pdf_file')}")
            if latest_log.get('status') == 'success':
                print(f"  ✓ 邮件发送成功")
            else:
                print(f"  ✗ 邮件发送失败: {latest_log.get('error_message')}")
    else:
        print(f"  获取日志失败: {response.text}")
    
    # 检查邮件发送统计
    print("\n4. 检查邮件发送统计...")
    response = requests.get(f"{BASE_URL}/api/email/statistics")
    if response.status_code == 200:
        stats = response.json()
        print(f"  总发送次数: {stats.get('total_logs')}")
        print(f"  成功次数: {stats.get('success_logs')}")
        print(f"  失败次数: {stats.get('failure_logs')}")
        print(f"  成功率: {stats.get('success_rate', 0)}%")
    else:
        print(f"  获取统计失败: {response.text}")

if __name__ == "__main__":
    try:
        test_send_test_email()
        print("\n" + "=" * 50)
        print("测试完成")
        print("=" * 50)
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
