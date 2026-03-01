# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

from app import app

print("Testing API...")

with app.test_client() as client:
    response = client.post('/api/backtest/multi', json={
        "symbols": ["002009"],
        "start_date": "20200101",
        "end_date": "20251231",
        "strategy_type": "niu_huicai_atr"
    })
    
    print(f"Status: {response.status_code}")
    data = response.get_json()
    
    if data:
        print(f"Keys: {list(data.keys())}")
        print(f"Success: {data.get('success')}")
        if data.get('success'):
            trades = data.get('trades', [])
            print(f"Trades: {len(trades)}")
            for t in trades[:3]:
                print(f"  {t}")
        else:
            print(f"Message: {data.get('message')}")
    else:
        print("No data returned!")
