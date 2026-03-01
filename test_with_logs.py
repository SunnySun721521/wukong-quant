# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

from app import app
import io
import logging

# Capture logs
log_capture = io.StringIO()
handler = logging.StreamHandler(log_capture)
handler.setLevel(logging.DEBUG)

# Get the Flask app logger
flask_logger = logging.getLogger('werkzeug')
flask_logger.addHandler(handler)

with app.test_client() as client:
    response = client.post('/api/backtest/multi', json={
        "symbols": ["002009"],
        "start_date": "20200101",
        "end_date": "20251231",
        "strategy_type": "niu_huicai_atr"
    })
    
    print(f"Status: {response.status_code}")
    
    data = response.get_json()
    print(f"Keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
    print(f"Success: {data.get('success') if isinstance(data, dict) else data}")
    
    if data.get('success'):
        trades = data.get('trades', [])
        print(f"Trades count: {len(trades)}")
        for t in trades[:10]:
            print(f"  {t}")
    else:
        print(f"Message: {data.get('message')}")

print("\n=== Server Logs ===")
print(log_capture.getvalue())
