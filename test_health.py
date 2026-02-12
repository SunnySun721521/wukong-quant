#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_health():
    """测试健康检查端点"""
    url = "http://127.0.0.1:5006/health"
    
    print("测试健康检查端点...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    success = test_health()
    print(f"\n结果: {'成功' if success else '失败'}")
