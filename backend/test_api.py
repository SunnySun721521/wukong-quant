import requests

# 测试默认值
print("测试默认值:")
r = requests.get('http://127.0.0.1:5006/api/plan/position')
print(f"状态码: {r.status_code}")
data = r.json()
print(f"可用现金: {data['available_cash']}")
print(f"总资产: {data['total_assets']}")
print()

# 测试自定义值
print("测试自定义值:")
r = requests.get('http://127.0.0.1:5006/api/plan/position?available_cash=200000')
print(f"状态码: {r.status_code}")
data = r.json()
print(f"可用现金: {data['available_cash']}")
print(f"总资产: {data['total_assets']}")
print()

# 测试另一个自定义值
print("测试另一个自定义值:")
r = requests.get('http://127.0.0.1:5006/api/plan/position?available_cash=300000')
print(f"状态码: {r.status_code}")
data = r.json()
print(f"可用现金: {data['available_cash']}")
print(f"总资产: {data['total_assets']}")
