import requests
import time

print("=" * 60)
print("测试调仓建议API - 简化版")
print("=" * 60)

url = 'http://localhost:5006/api/plan/adjustment'

try:
    print(f"\n正在调用: {url}")
    r = requests.get(url, timeout=10)
    print(f"状态码: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"\n更新时间: {data.get('update_time', 'N/A')}")
        
        suggestions = data.get('suggestions', [])
        print(f"\n调仓建议数量: {len(suggestions)}")
        
        if suggestions:
            print("\n调仓建议列表:")
            for i, s in enumerate(suggestions, 1):
                print(f"{i}. {s['symbol']} {s['name']} - {s['action_text']}")
                
                if s['symbol'] in ['600519', '000858']:
                    print(f"   ⚠️ 警告: 发现不在股票池中的股票 {s['symbol']} {s['name']}")
        else:
            print("\n✓ 暂无调仓建议")
            
    else:
        print(f"请求失败: {r.status_code}")
        print(r.text)
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
