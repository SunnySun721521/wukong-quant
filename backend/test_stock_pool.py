import requests
import json

# 测试股票池管理功能
print("测试股票池管理功能...")

# 1. 检查当前股票池状态
print("\n1. 检查当前股票池状态:")
response = requests.get("http://127.0.0.1:5006/api/stockpool/info")
if response.status_code == 200:
    data = response.json()
    print(f"当前股票池: {data['current_pool']}")
    print(f"股票池大小: {data['pool_size']}")
else:
    print(f"获取股票池信息失败，状态码: {response.status_code}")

# 2. 更新股票池，导入新的股票数据
print("\n2. 更新股票池，导入新的股票数据:")
test_stocks = ['600519', '000858', '002371', '601318', '600036']  # 茅台、五粮液、北方华创 + 中国平安、招商银行
update_data = {"stocks": test_stocks, "adjust": False}
response = requests.post("http://127.0.0.1:5006/api/stockpool/update", json=update_data)
if response.status_code == 200:
    data = response.json()
    print(f"更新后的股票池: {data['current_pool']}")
    print(f"消息: {data['message']}")
else:
    print(f"更新股票池失败，状态码: {response.status_code}")
    print(f"错误信息: {response.text}")

# 3. 再次检查股票池状态，确保更新成功
print("\n3. 再次检查股票池状态:")
response = requests.get("http://127.0.0.1:5006/api/stockpool/info")
if response.status_code == 200:
    data = response.json()
    print(f"当前股票池: {data['current_pool']}")
    print(f"股票池大小: {data['pool_size']}")
else:
    print(f"获取股票池信息失败，状态码: {response.status_code}")
