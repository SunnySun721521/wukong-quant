import urllib.request

# Test API to get backtest pool
print("Getting backtest pool...")
try:
    req = urllib.request.Request("http://127.0.0.1:5006/api/backtest/pool", headers={})
    with urllib.request.urlopen(req, timeout=5) as response:
        result = response.read().decode('utf-8')
        print(f"Response: {result}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

# Try getting stock list
print("\nGetting stock list...")
try:
    req = urllib.request.Request("http://127.0.0.1:5006/api/stocks", headers={})
    with urllib.request.urlopen(req, timeout=5) as response:
        result = response.read().decode('utf-8')
        print(f"Response: {result[:500]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
