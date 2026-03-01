# -*- coding: utf-8 -*-
import requests

# 测试 /api/bpool/update
try:
    r = requests.post('http://localhost:5006/api/bpool/update', json={'stocks': ['000001', '000002']})
    print(f"bpool 状态码: {r.status_code}")
    print(f"bpool 响应: {r.text[:200]}")
except Exception as e:
    print(f"bpool 错误: {e}")

print()

# 测试 /api/stockpool/update  
try:
    r = requests.post('http://localhost:5006/api/stockpool/update', json={'stocks': ['000001', '000002'], 'adjust': False})
    print(f"stockpool 状态码: {r.status_code}")
    print(f"stockpool 响应: {r.text[:200]}")
except Exception as e:
    print(f"stockpool 错误: {e}")
