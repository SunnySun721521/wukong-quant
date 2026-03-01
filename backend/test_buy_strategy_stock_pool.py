import requests
import json

# 测试买入策略API是否从默认股票池获取数据
print("测试买入策略API是否从默认股票池获取数据...")

# 1. 检查当前股票池状态
print("\n1. 检查当前股票池状态:")
response = requests.get("http://127.0.0.1:5006/api/stockpool/info")
if response.status_code == 200:
    data = response.json()
    print(f"当前股票池: {data['current_pool']}")
    print(f"股票池大小: {data['pool_size']}")
    print(f"完整响应: {json.dumps(data, ensure_ascii=False)}")
else:
    print(f"获取股票池信息失败，状态码: {response.status_code}")

# 2. 获取买入建议
print("\n2. 获取买入建议:")
response = requests.get("http://127.0.0.1:5006/api/plan/buy")
if response.status_code == 200:
    data = response.json()
    print(f"完整响应: {json.dumps(data, ensure_ascii=False)}")
    print(f"买入建议数量: {len(data.get('suggestions', []))}")
    print("\n买入建议详情:")
    for suggestion in data.get('suggestions', []):
        print(f"股票: {suggestion.get('name', '未知')} ({suggestion.get('symbol', '未知')})")
        print(f"建议: {suggestion.get('action_text', '未知')}")
        print(f"理由: {suggestion.get('reason', '未知')}")
        print(f"价格区间: {suggestion.get('price_range', '未知')}")
        print(f"止损位: {suggestion.get('stop_loss', '未知')}")
        print()
else:
    print(f"获取买入建议失败，状态码: {response.status_code}")
    print(f"错误信息: {response.text}")
