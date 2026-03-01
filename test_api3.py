import urllib.request
import urllib.parse
import json

url = "http://127.0.0.1:5006/api/backtest/multi"
data = {
    "symbols": ["002009"],
    "start_date": "20200101", 
    "end_date": "20201231",
    "strategy_type": "niu_huicai"
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

print("Testing backtest API...")
try:
    with urllib.request.urlopen(req, timeout=60) as response:
        result = response.read().decode('utf-8')
        print(f"Status: {response.status}")
        print(f"Response: {result[:500]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
