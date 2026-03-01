import requests
import json

# Test backtest API
url = "http://127.0.0.1:5006/api/backtest/multi"
data = {
    "symbols": ["002009"],
    "start_date": "20200101",
    "end_date": "20201231",
    "fast_period": 5,
    "slow_period": 20,
    "initial_cash": 100000,
    "transaction_cost": 0.3,
    "strategy_type": "niu_huicai"
}

print("Testing backtest API...")
try:
    r = requests.post(url, json=data, timeout=60)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
