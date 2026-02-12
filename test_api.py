import http.client
import json

# 测试添加股票API
def test_add_stock(stock_code):
    conn = http.client.HTTPConnection("localhost", 5001)
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        'stock_code': stock_code
    }
    
    json_data = json.dumps(data)
    
    try:
        conn.request("POST", "/api/stockpool/add", json_data, headers)
        response = conn.getresponse()
        
        print(f"\n测试添加股票 {stock_code}:")
        print(f"状态码: {response.status}")
        print(f"状态: {response.reason}")
        
        if response.status == 200:
            response_data = response.read().decode()
            print(f"响应数据: {response_data}")
        else:
            print(f"错误信息: {response.read().decode()}")
            
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        conn.close()

# 测试获取股票池信息
def test_get_stock_pool():
    conn = http.client.HTTPConnection("localhost", 5001)
    
    try:
        conn.request("GET", "/api/stockpool/info")
        response = conn.getresponse()
        
        print(f"\n测试获取股票池信息:")
        print(f"状态码: {response.status}")
        print(f"状态: {response.reason}")
        
        if response.status == 200:
            response_data = response.read().decode()
            data = json.loads(response_data)
            print(f"股票池大小: {len(data.get('current_pool', []))}")
            print(f"股票池: {data.get('current_pool', [])}")
        else:
            print(f"错误信息: {response.read().decode()}")
            
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("开始测试API...")
    
    # 测试获取股票池信息
    test_get_stock_pool()
    
    # 测试添加股票
    test_add_stock("000002")  # 万科A
    test_add_stock("600000")  # 浦发银行
    test_add_stock("301269")  # 华大九天
    
    # 再次获取股票池信息，验证添加结果
    test_get_stock_pool()
    
    print("\n测试完成!")