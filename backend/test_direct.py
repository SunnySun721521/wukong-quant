import requests
import json

url = 'http://localhost:5006/api/plan/adjustment'
try:
    r = requests.get(url, timeout=10)
    if r.status_code == 200:
        data = r.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
