# -*- coding: utf-8 -*-
import urllib.request
import json

url = 'http://localhost:5006/api/plan/adjustment'
try:
    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        print(f"状态码: {response.status}")
        print(f"建议数量: {len(data.get('suggestions', []))}")
        for s in data.get('suggestions', []):
            print(f"  {s.get('symbol')} - {s.get('name')}: {s.get('reason')}")
except Exception as e:
    print(f"错误: {e}")
