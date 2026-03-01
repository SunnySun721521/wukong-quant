# -*- coding: utf-8 -*-
import requests

try:
    r = requests.get('http://localhost:5006/api/plan/adjustment')
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.text[:1000]}")
except Exception as e:
    print(f"错误: {e}")
