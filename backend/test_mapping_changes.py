import requests
import json

print("=" * 60)
print("测试后端映射表修改")
print("=" * 60)

# 测试 2: 调仓建议 API
print("\n1. 测试调仓建议 API (/api/plan/adjustment)")
try:
    r = requests.get('http://localhost:5006/api/plan/adjustment')
    data = json.loads(r.text)
    print(f"   状态码: {r.status_code}")
    if 'suggestions' in data:
        print(f"   建议数量: {len(data['suggestions'])}")
        for suggestion in data['suggestions'][:2]:
            print(f"   - {suggestion['symbol']}: {suggestion['name']}")
except Exception as e:
    print(f"   错误: {e}")

# 测试 3: 买入策略 API
print("\n2. 测试买入策略 API (/api/plan/buy)")
try:
    r = requests.get('http://localhost:5006/api/plan/buy')
    data = json.loads(r.text)
    print(f"   状态码: {r.status_code}")
    if 'suggestions' in data:
        print(f"   建议数量: {len(data['suggestions'])}")
        for suggestion in data['suggestions'][:2]:
            print(f"   - {suggestion['symbol']}: {suggestion['name']}")
except Exception as e:
    print(f"   错误: {e}")

# 测试 4: 新闻 API
print("\n3. 测试新闻 API (/api/plan/news)")
try:
    r = requests.get('http://localhost:5006/api/plan/news')
    data = json.loads(r.text)
    print(f"   状态码: {r.status_code}")
    if 'news' in data:
        print(f"   新闻数量: {len(data['news'])}")
        for news in data['news'][:2]:
            print(f"   - {news['title']}")
            if 'related_stocks' in news:
                print(f"     相关股票: {news['related_stocks']}")
except Exception as e:
    print(f"   错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
