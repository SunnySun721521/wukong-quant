# -*- coding: utf-8 -*-
import subprocess
import requests
import time
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

print("Server starting...")
time.sleep(8)

print("Calling backtest API...")
try:
    resp = requests.post(
        "http://127.0.0.1:5006/api/backtest/multi",
        json={
            "symbols": ["002009"],
            "start_date": "20200101",
            "end_date": "20231231",
            "strategy_type": "niu_huicai_atr"
        },
        timeout=120
    )
    print(f"API Status: {resp.status_code}")
except Exception as e:
    print(f"API Error: {e}")

time.sleep(5)
proc.terminate()

print("\n=== Server Output ===")
