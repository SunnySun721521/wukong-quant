# -*- coding: utf-8 -*-
import urllib.request
import json
import ssl

url = "http://127.0.0.1:5006/api/backtest/multi"
data = json.dumps({
    "symbols": ["002009"],
    "start_date": "20200101",
    "end_date": "20231231",
    "strategy_type": "niu_huicai_atr"
}).encode('utf-8')

req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=120, context=ctx) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("OK")
        if 'result' in result:
            r = result['result']
            print("Trades:", r.get('total_trades', 0))
except Exception as e:
    print("Error:", str(e)[:200])
