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
    
    print("Status:", response.status_code)
    data = response.get_json()
    
    if data:
        print("Keys:", list(data.keys()))
        
        # The result is nested under 'result' key
        if 'result' in data:
            result = data['result']
            print("Result keys:", list(result.keys()) if isinstance(result, dict) else "Not a dict")
            
            if isinstance(result, dict):
                trades = result.get('trades', [])
                print("Trades count:", len(trades))
                if trades:
                    for t in trades[:5]:
                        print("  Trade:", t)
        elif 'error' in data:
            print("Error:", data.get('error'))
            print("Traceback:", data.get('traceback', 'N/A')[:500])
        else:
            print("Full response:", data)
    else:
        print("No data returned!")
