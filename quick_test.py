import requests
import json

url = "http://127.0.0.1:5006/api/backtest/multi"
data = {
    "symbols": ["002009"],
    "start_date": "20200101",
    "end_date": "20251231",
    "strategy_type": "niu_huicai_atr"
}

print("Calling backtest API...")
r = requests.post(url, json=data, timeout=120)
print(f"Status: {r.status_code}")

result = r.json()
print(f"Success: {result.get('success')}")

if result.get('success'):
    trades = result.get('trades', [])
    print(f"Total trades: {len(trades)}")
    for t in trades[:10]:
        print(f"  {t.get('date')} {t.get('type')} {t.get('symbol')} {t.get('price')}")
else:
    print(f"Error: {result.get('message')}")
