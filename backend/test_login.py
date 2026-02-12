#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

print("=== 测试登录功能 ===")

# 测试1: 正确的用户名和密码
print("\n1. 测试正确的用户名和密码:")
data = {
    "username": "admin",
    "password": "libo0519"
}

try:
    response = requests.post('http://127.0.0.1:5006/api/login', json=data)
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('success'):
        print("✅ 登录成功！")
    else:
        print(f"❌ 登录失败: {result.get('message')}")
except Exception as e:
    print(f"请求异常: {e}")

# 测试2: 错误的用户名和密码
print("\n2. 测试错误的用户名和密码:")
data = {
    "username": "wrong",
    "password": "wrong"
}

try:
    response = requests.post('http://127.0.0.1:5006/api/login', json=data)
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('success'):
        print("❌ 不应该登录成功！")
    else:
        print("✅ 正确拒绝了错误的用户名和密码")
except Exception as e:
    print(f"请求异常: {e}")

# 测试3: 空的用户名和密码
print("\n3. 测试空的用户名和密码:")
data = {
    "username": "",
    "password": ""
}

try:
    response = requests.post('http://127.0.0.1:5006/api/login', json=data)
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('success'):
        print("❌ 不应该登录成功！")
    else:
        print("✅ 正确拒绝了空的用户名和密码")
except Exception as e:
    print(f"请求异常: {e}")

print("\n=== 测试完成 ===")