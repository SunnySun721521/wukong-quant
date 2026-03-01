import urllib.request

# Test with moving_average strategy (simpler)
print("Test 1: moving_average strategy...")
data1 = b'{"symbols":["002009"],"start_date":"20200101","end_date":"20200301","strategy_type":"moving_average","initial_cash":100000,"transaction_cost":0.3}'
req1 = urllib.request.Request("http://127.0.0.1:5006/api/backtest/multi", data=data1, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req1, timeout=30) as response:
        print(f"Status: {response.status}")
        print(f"Response: {response.read().decode('utf-8')[:200]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

print("\n" + "="*50)

# Test with niu_huicai
print("Test 2: niu_huicai strategy...")
data2 = b'{"symbols":["002009"],"start_date":"20200101","end_date":"20200301","strategy_type":"niu_huicai","initial_cash":100000,"transaction_cost":0.3}'
req2 = urllib.request.Request("http://127.0.0.1:5006/api/backtest/multi", data=data2, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req2, timeout=30) as response:
        print(f"Status: {response.status}")
        print(f"Response: {response.read().decode('utf-8')[:200]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
