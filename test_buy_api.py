import requests
print("Testing buy API...")

try:
    r = requests.get("http://127.0.0.1:5006/api/plan/buy", timeout=30)
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Keys: {list(data.keys())}")
    
    if 'error' in data:
        print(f"Error: {data['error']}")
    elif 'suggestions' in data:
        print(f"Suggestions count: {len(data['suggestions'])}")
        if data['suggestions']:
            for s in data['suggestions'][:3]:
                print(f"  - {s}")
        else:
            print("  (empty)")
    else:
        print(f"Full response: {data}")
except Exception as e:
    print(f"Error: {e}")
