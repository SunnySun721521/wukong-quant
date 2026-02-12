import requests
import json

# 清除缓存并测试买入策略API
print("清除缓存并测试买入策略API...")

# 1. 发送请求到买入策略API，强制刷新缓存
print("\n1. 测试买入策略API（强制刷新缓存）:")
response = requests.get("http://127.0.0.1:5006/api/plan/buy")
if response.status_code == 200:
    data = response.json()
    print(f"状态: {data.get('status', '未知')}")
    print(f"消息: {data.get('message', '未知')}")
    print(f"更新时间: {data.get('update_time', '未知')}")
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
