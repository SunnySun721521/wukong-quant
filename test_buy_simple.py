#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_buy_api_simple():
    """简单测试买入API"""
    
    # 测试数据
    test_data = {
        "symbol": "002371",
        "name": "北方华创",
        "quantity": 100,
        "cost_price": 472.23
    }
    
    url = "http://127.0.0.1:5006/api/plan/position"
    
    print("发送买入请求...")
    print(f"URL: {url}")
    print(f"数据: {json.dumps(test_data, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"\n状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        return response.status_code == 201
        
    except Exception as e:
        print(f"\n错误: {e}")
        return False

if __name__ == "__main__":
    success = test_buy_api_simple()
    print(f"\n结果: {'成功' if success else '失败'}")
