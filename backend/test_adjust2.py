# -*- coding: utf-8 -*-
import requests

try:
    r = requests.get('http://localhost:5006/api/plan/adjustment')
    print(f"状态码: {r.status_code}")
    data = r.json()
    print(f"建议数量: {len(data.get('suggestions', []))}")
    for s in data.get('suggestions', []):
        print(f"  {s.get('symbol')} - {s.get('name')}: {s.get('reason')}")
except Exception as e:
    print(f"错误: {e}")
