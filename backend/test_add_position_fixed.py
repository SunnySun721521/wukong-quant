#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

print("=== 测试添加持仓003816 - 验证修复效果 ===")

# 模拟添加持仓的请求
data = {
    "symbol": "003816",
    "quantity": 100,
    "cost_price": 3.92
}

try:
    response = requests.post('http://127.0.0.1:5006/api/plan/position', json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if 'message' in result:
            print(f"\n消息: {result['message']}")
        
        if 'position' in result:
            position = result['position']
            print(f"\n持仓信息:")
            print(f"  股票代码: {position.get('symbol', 'N/A')}")
            print(f"  股票名称: {position.get('name', 'N/A')}")
            print(f"  持仓数量: {position.get('quantity', 'N/A')}")
            print(f"  成本价: {position.get('cost_price', 'N/A')}")
            print(f"  当前价: {position.get('current_price', 'N/A')}")
            
            if position.get('name') == '中国广核':
                print(f"\n✅ 成功！股票名称正确显示为'中国广核'")
            else:
                print(f"\n❌ 失败！股票名称显示为'{position.get('name')}'，应该是'中国广核'")
    else:
        print(f"请求失败: {response.text}")
        
except Exception as e:
    print(f"请求异常: {e}")

print("\n=== 测试完成 ===")