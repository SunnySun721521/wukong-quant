# -*- coding: utf-8 -*-
import requests

try:
    r = requests.post('http://localhost:5006/api/backtestpool/update', json={'stocks': ['000001', '000002']})
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.text}")
except Exception as e:
    print(f"错误: {e}")
