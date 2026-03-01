import requests
import json

print("测试调仓建议 API")
try:
    r = requests.get('http://localhost:5006/api/plan/adjustment', timeout=10)
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"建议数量: {len(data.get('suggestions', []))}")
        for s in data.get('suggestions', [])[:3]:
            print(f"  {s['symbol']}: {s['name']}")
    else:
        print(f"响应内容: {r.text[:200]}")
except Exception as e:
    print(f"错误: {e}")

print("\n测试买入策略 API")
try:
    r = requests.get('http://localhost:5006/api/plan/buy', timeout=10)
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"建议数量: {len(data.get('suggestions', []))}")
        for s in data.get('suggestions', [])[:3]:
            print(f"  {s['symbol']}: {s['name']}")
    else:
        print(f"响应内容: {r.text[:200]}")
except Exception as e:
    print(f"错误: {e}")

print("\n测试新闻 API")
try:
    r = requests.get('http://localhost:5006/api/plan/news', timeout=10)
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"新闻数量: {len(data.get('news', []))}")
        for n in data.get('news', [])[:2]:
            print(f"  {n['title']}")
    else:
        print(f"响应内容: {r.text[:200]}")
except Exception as e:
    print(f"错误: {e}")
