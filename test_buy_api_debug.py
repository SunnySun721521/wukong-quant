#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_buy_api():
    """测试买入API"""
    
    # 测试数据
    test_data = {
        "symbol": "002371",
        "name": "北方华创",
        "quantity": 100,
        "cost_price": 200.0
    }
    
    url = "http://127.0.0.1:5006/api/plan/position"
    
    print("=" * 60)
    print("测试买入API")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print()
        
        try:
            result = response.json()
            print(f"响应内容:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except:
            print(f"响应内容（非JSON）:")
            print(response.text)
        
        print()
        
        if response.status_code == 201:
            print("✅ 买入成功！")
        else:
            print(f"❌ 买入失败，状态码: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请检查服务器是否运行")
    except Exception as e:
        print(f"❌ 发生异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    test_buy_api()
