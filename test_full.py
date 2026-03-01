import urllib.request

print("Testing backtest with full params...")
data = b'{"symbols":["002009"],"start_date":"20200101","end_date":"20201231","strategy_type":"niu_huicai","initial_cash":100000,"transaction_cost":0.3}'

req = urllib.request.Request("http://127.0.0.1:5006/api/backtest/multi", data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req, timeout=90) as response:
        print(f"Status: {response.status}")
        result = response.read().decode('utf-8')
        print(f"Response: {result[:500]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
