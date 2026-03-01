# -*- coding: utf-8 -*-
import urllib.request
import json

try:
    print("测试 /api/plan/test...")
    url = "http://localhost:5006/api/plan/test"
    with urllib.request.urlopen(url, timeout=5) as response:
        data = response.read().decode('utf-8')
        print(f"响应: {data}")
        
    print("\n测试 /api/plan/market-status...")
    url = "http://localhost:5006/api/plan/market-status"
    with urllib.request.urlopen(url, timeout=5) as response:
        data = response.read().decode('utf-8')
        print(f"响应: {data[:200]}")
        
    print("\n测试 /api/plan/adjustment...")
    url = "http://localhost:5006/api/plan/adjustment"
    with urllib.request.urlopen(url, timeout=5) as response:
        data = response.read().decode('utf-8')
        print(f"响应: {data[:500]}")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
