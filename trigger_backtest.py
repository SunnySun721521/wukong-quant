# -*- coding: utf-8 -*-
import urllib.request
import json

url = "http://127.0.0.1:5006/api/backtest/multi"
data = {
    "symbols": ["002009"],
    "start_date": "20200101",
    "end_date": "20251231",
    "strategy_type": "niu_huicai_atr"
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(req, timeout=120, context=ctx)
    result = json.loads(response.read().decode('utf-8'))
    print("OK")
except Exception as e:
    print("Error:", str(e)[:200])
