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
print(f"Content-Type: {r.headers.get('Content-Type')}")

# Print raw response
text = r.text
print(f"\nRaw response (first 500 chars):\n{text[:500]}")

# Try to parse as JSON
try:
    result = r.json()
    print(f"\nJSON keys: {result.keys()}")
except Exception as e:
    print(f"JSON parse error: {e}")
