import requests
print("Testing market-status API...")

endpoints = [
    "/api/dataupdateconfig",
    "/api/plan/market-status",
    "/api/plan/position",
    "/api/plan/adjustment"
]

for ep in endpoints:
    try:
        r = requests.get(f"http://127.0.0.1:5006{ep}", timeout=10)
        print(f"{ep}: Status={r.status_code}")
        data = r.json()
        if 'error' in data:
            print(f"  Error: {data['error']}")
        else:
            print(f"  Keys: {list(data.keys())[:5]}")
    except Exception as e:
        print(f"{ep}: Error - {e}")
