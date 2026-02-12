import requests

r = requests.get('http://localhost:5006/api/plan/adjustment', timeout=10)
print(f"状态码: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"建议数量: {len(data.get('suggestions', []))}")
    for s in data.get('suggestions', [])[:3]:
        print(f"  {s['symbol']}: {s['name']}")
