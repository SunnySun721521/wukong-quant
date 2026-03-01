# -*- coding: utf-8 -*-
import urllib.request
import json
import time
import subprocess
import sys
import os

os.chdir(r"d:\trae\备份悟空52224\backend")

proc = subprocess.Popen(
    [sys.executable, "app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    bufsize=1,
    encoding='utf-8',
    errors='replace'
)

print("Server starting... wait 8 seconds")
time.sleep(8)

print("Calling backtest API...")
try:
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostnaame = False
    ctx.verify_mode = ssl.CERT_NONE
    
    url = "http://127.0.0.1:5006/api/backtest/multi"
    data = json.dumps({
        "symbols": ["002009"],
        "start_date": "20200101",
        "end_date": "20251231",
        "strategy_type": "niu_huicai_atr"
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(req, timeout=120, context=ctx)
    result = json.loads(response.read().decode('utf-8'))
    print("API Status: OK")
except Exception as e:
    print(f"API Error: {e}")

print("Wait 10 seconds for logs...")
time.sleep(10)

proc.terminate()

print("\n=== Server Output ===")
for line in proc.stdout:
    print(line, end='')
