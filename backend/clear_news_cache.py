import requests

def clear_news_cache():
    """清除新闻API的缓存"""
    print("清除新闻API缓存...")
    
    # 由于缓存是内存中的，最简单的方法是重启服务器
    # 但我们可以通过调用API来更新缓存
    try:
        # 调用新闻API，这会更新缓存
        response = requests.get("http://127.0.0.1:5006/api/plan/news")
        if response.status_code == 200:
            data = response.json()
            print(f"新闻API调用成功，已更新缓存")
            print(f"新闻数量: {len(data.get('news', []))}")
            print(f"更新时间: {data.get('update_time', '未知')}")
            return True
        else:
            print(f"新闻API调用失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"清除缓存失败: {e}")
        return False

if __name__ == "__main__":
    clear_news_cache()
