#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

url = 'http://127.0.0.1:5002/api/backtest/multi'
data = {
    'symbols': ['600519', '000858', '002371', '002415', '002236'],
    'start_date': '20240101',
    'end_date': '20250111',
    'fast_period': 5,
    'slow_period': 20
}

print(f"发送请求到: {url}")
print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")

try:
    response = requests.post(url, json=data, timeout=60)
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n回测成功！")
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print(f"\n回测失败！")
except Exception as e:
    print(f"\n发生异常: {e}")
    import traceback
    traceback.print_exc()