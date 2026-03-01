# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json
import ssl

url = "http://127.0.0.1:5006/api/backtest/multi"
data = {
    "symbols": ["002009"],
    "start_date": "20200101",
    "end_date": "20231231",
    "strategy_type": "niu_huicai_atr"
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    response = urllib.request.urlopen(req, timeout=120, context=ssl._create_unverified_context())
    result = json.loads(response.read().decode('utf-8'))
    print("Status: OK")
    if 'result' in result:
        r = result['result']
        print("Total trades:", r.get('total_trades', 0))
        if 'individual_results' in r:
            for stock_result in r['individual_results']:
                print(f"Stock: {stock_result.get('symbol')}, Trades: {len(stock_result.get('trades', []))}")
                for trade in stock_result.get('trades', []):
                    print(f"  {trade.get('date')} {trade.get('type')} {trade.get('price')}")
except Exception as e:
    print("Error:", e)
