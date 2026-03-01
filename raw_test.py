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
    text = response.get_data(as_text=True)
    print("Raw response (first 800 chars):")
    print(text[:800])
