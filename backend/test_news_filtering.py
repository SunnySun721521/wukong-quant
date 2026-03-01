import requests
import json

def test_news_filtering():
    """测试新闻过滤功能"""
    print("测试新闻过滤功能...")
    print("=" * 60)
    
    # 1. 获取持仓数据
    print("\n1. 获取持仓数据:")
    response = requests.get("http://127.0.0.1:5006/api/plan/position")
    if response.status_code == 200:
        data = response.json()
        positions = data.get('positions', [])
        print(f"持仓数量: {len(positions)}")
        print("持仓明细:")
        for pos in positions:
            print(f"  {pos['symbol']} {pos['name']}")
    else:
        print(f"获取持仓数据失败，状态码: {response.status_code}")
        return
    
    # 2. 获取买入建议
    print("\n2. 获取买入建议:")
    response = requests.get("http://127.0.0.1:5006/api/plan/buy")
    if response.status_code == 200:
        data = response.json()
        suggestions = data.get('suggestions', [])
        print(f"买入建议数量: {len(suggestions)}")
        print("买入建议明细:")
        for suggestion in suggestions:
            print(f"  {suggestion['symbol']} {suggestion['name']} - {suggestion['action_text']}")
    else:
        print(f"获取买入建议失败，状态码: {response.status_code}")
        return
    
    # 3. 获取新闻
    print("\n3. 获取新闻:")
    response = requests.get("http://127.0.0.1:5006/api/plan/news")
    if response.status_code == 200:
        data = response.json()
        news_list = data.get('news', [])
        print(f"新闻数量: {len(news_list)}")
        print(f"更新时间: {data.get('update_time', '未知')}")
        print("\n新闻明细:")
        for i, news in enumerate(news_list, 1):
            print(f"\n{i}. {news['title']}")
            print(f"   时间: {news['time']}")
            print(f"   来源: {news['source']}")
            print(f"   内容: {news['content']}")
            if 'related_stocks' in news:
                print(f"   相关股票: {news['related_stocks']}")
    else:
        print(f"获取新闻失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
    
    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    test_news_filtering()
