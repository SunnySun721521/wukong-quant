import requests
import time

print("Testing buy API with longer timeout...")

try:
    print("Calling API...")
    r = requests.get("http://127.0.0.1:5006/api/plan/buy", timeout=60)
    print(f"Status: {r.status_code}")
    print(f"Content length: {len(r.content)} bytes")
    
    data = r.json()
    print(f"Keys: {list(data.keys())}")
    
    if 'error' in data:
        print(f"Error: {data['error']}")
    elif 'suggestions' in data:
        print(f"Suggestions count: {len(data['suggestions'])}")
    else:
        print(f"Response: {data}")
        
except requests.exceptions.Timeout:
    print("Request timeout - API is taking too long")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
