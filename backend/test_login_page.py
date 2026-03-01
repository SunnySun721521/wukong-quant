#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

print("=== 测试登录页面访问 ===")

# 测试访问登录页面
try:
    response = requests.get('http://127.0.0.1:5006/login.html')
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 登录页面访问成功！")
        if 'login' in response.text.lower():
            print("✅ 页面内容正确（包含login）")
        else:
            print("❌ 页面内容不正确")
    else:
        print(f"❌ 登录页面访问失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}")
        
except Exception as e:
    print(f"请求异常: {e}")

print("\n=== 测试完成 ===")