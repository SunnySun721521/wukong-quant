# -*- coding: utf-8 -*-
import requests
import json
import sys

try:
    print("开始测试 API...")
    r = requests.get('http://localhost:5006/api/plan/adjustment', timeout=10)
    print(f"状态码: {r.status_code}")
    data = r.json()
    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
