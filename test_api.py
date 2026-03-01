import requests
import json

url = "http://127.0.0.1:5006/api/backtest/multi"
data = {
    "symbols": ["002009"],
    "start_date": "20200101",
    "end_date": "20251231",
    "strategy_type": "niu_huicai_atr"
}

print("Making request...")
try:
    r = requests.post(url, json=data, timeout=120)
    print("Status:", r.status_code)
    result = r.json()
    if result.get('success'):
        print("Trades:", len(result.get('trades', [])))
    else:
        print("Error:", result.get('message', 'no message'))
except Exception as e:
    print("Exception:", e)
