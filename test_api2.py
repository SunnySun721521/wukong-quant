import http.client
import json

# 测试添加股票API
def test_add_stock(stock_code):
    conn = http.client.HTTPConnection("localhost", 5001)
    headers = {'Content-Type': 'application/json'}
    data = {'stock_code': stock_code}
    json_data = json.dumps(data)
    
    try:
        conn.request("POST", "/api/stockpool/add", json_data, headers)
        response = conn.getresponse()
        print(f"\n测试添加股票 {stock_code}:")
        print(f"状态码: {response.status}")
        print(f"状态: {response.reason}")
        response_data = response.read().decode()
        print(f"响应: {response_data}")
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
        response_data = response.read().decode()
        data = json.loads(response_data)
        print(f"股票池: {data.get('current_pool', [])}")
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("开始测试API...")
    test_get_stock_pool()
    test_add_stock("000002")
    test_get_stock_pool()
    print("测试完成!")