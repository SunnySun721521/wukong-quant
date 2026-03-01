# -*- coding: utf-8 -*-
import urllib.request
import json
import time

stocks = [
    "002009", "600519", "000858", "002371", "600036",
    "000001", "600030", "600887", "601318", "601166",
    "000333", "600104", "600050", "601288", "601398",
    "600009", "600016", "600030", "601012", "601888",
    "603259", "603501", "300750", "300059", "002594"
]

stocks = list(set(stocks))  # Remove duplicates
print(f"Testing {len(stocks)} stocks with moving_average strategy")

results = []

for i, symbol in enumerate(stocks):
    print(f"[{i+1}/{len(stocks)}] Testing {symbol}...", end=" ", flush=True)
    
    data = json.dumps({
        "symbols": [symbol],
        "start_date": "20240101",
        "end_date": "20260228",
        "strategy_type": "moving_average",
        "initial_cash": 100000,
        "transaction_cost": 0.3
    }).encode('utf-8')
    
    req = urllib.request.Request(
        "http://127.0.0.1:5006/api/backtest/multi",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('result'):
                win_rate = result['result'].get('win_rate', 0) * 100
                total_trades = result['result'].get('total_trades', 0)
                total_return = result['result'].get('total_return', 0) * 100
                print(f"Win Rate: {win_rate:.1f}%, Trades: {total_trades}, Return: {total_return:.1f}%")
                results.append({
                    'symbol': symbol,
                    'win_rate': win_rate,
                    'total_trades': total_trades,
                    'total_return': total_return
                })
            else:
                print(f"Error: {result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"Error: {e}")

# Sort by win rate
results.sort(key=lambda x: x['win_rate'], reverse=True)

print("\n" + "="*60)
print("WIN RATE RANKING (Moving Average Strategy)")
print("="*60)
for i, r in enumerate(results):
    print(f"{i+1}. {r['symbol']}: Win Rate={r['win_rate']:.1f}%, Trades={r['total_trades']}, Return={r['total_return']:.1f}%")
