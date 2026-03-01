#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

BASE_URL = "http://127.0.0.1:5006"

def test_email_config_api():
    """测试邮件配置API"""
    print("=" * 50)
    print("测试邮件配置API")
    print("=" * 50)
    
    # 获取邮件配置
    print("\n1. 获取邮件配置...")
    response = requests.get(f"{BASE_URL}/api/email/config")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        config = response.json()
        print(f"配置: {json.dumps(config, indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")
    
    # 验证邮件配置
    print("\n2. 验证邮件配置...")
    response = requests.post(f"{BASE_URL}/api/email/validate")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"验证结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")
    
    # 获取邮件发送日志
    print("\n3. 获取邮件发送日志...")
    response = requests.get(f"{BASE_URL}/api/email/logs")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        logs = response.json()
        print(f"日志数量: {len(logs.get('logs', []))}")
        if logs.get('logs'):
            print(f"最新日志: {json.dumps(logs['logs'][0], indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")
    
    # 获取邮件发送统计
    print("\n4. 获取邮件发送统计...")
    response = requests.get(f"{BASE_URL}/api/email/statistics")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"统计信息: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")

def test_scheduler_api():
    """测试定时任务API"""
    print("\n" + "=" * 50)
    print("测试定时任务API")
    print("=" * 50)
    
    # 获取定时任务配置
    print("\n1. 获取定时任务配置...")
    response = requests.get(f"{BASE_URL}/api/scheduler/config")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        config = response.json()
        print(f"配置: {json.dumps(config, indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")
    
    # 获取执行记录
    print("\n2. 获取执行记录...")
    response = requests.get(f"{BASE_URL}/api/scheduler/execution-log")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        logs = response.json()
        print(f"执行记录数量: {len(logs.get('executions', []))}")
        if logs.get('executions'):
            print(f"最新执行记录: {json.dumps(logs['executions'][0], indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")

if __name__ == "__main__":
    try:
        test_email_config_api()
        test_scheduler_api()
        print("\n" + "=" * 50)
        print("所有测试完成")
        print("=" * 50)
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
