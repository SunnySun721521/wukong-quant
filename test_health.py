import urllib.request

print("Testing health endpoint...")
try:
    with urllib.request.urlopen("http://127.0.0.1:5006/health", timeout=5) as response:
        print(f"Status: {response.status}")
        print(f"Response: {response.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

print("\nTesting backtest endpoint...")
try:
    data = b'{"symbols":["002009"],"start_date":"20200101","end_date":"20201231","strategy_type":"niu_huicai"}'
    req = urllib.request.Request("http://127.0.0.1:5006/api/backtest/multi", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as response:
        print(f"Status: {response.status}")
        print(f"Response: {response.read().decode('utf-8')[:300]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
