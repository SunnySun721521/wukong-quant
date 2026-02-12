import requests
import json

BASE_URL = 'http://127.0.0.1:5006'

def test_email_recipients_api():
    """测试接收邮箱管理API"""
    print("=" * 50)
    print("测试接收邮箱管理API")
    print("=" * 50)
    
    # 1. 测试获取接收邮箱列表
    print("\n1. 测试获取接收邮箱列表")
    response = requests.get(f'{BASE_URL}/api/email/recipients')
    data = response.json()
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    # 2. 测试添加接收邮箱
    print("\n2. 测试添加接收邮箱")
    test_recipients = [
        {
            'email_address': 'api_test1@example.com',
            'name': 'API测试用户1',
            'description': 'API测试邮箱1',
            'is_active': True
        },
        {
            'email_address': 'api_test2@example.com',
            'name': 'API测试用户2',
            'description': 'API测试邮箱2',
            'is_active': True
        }
    ]
    
    for recipient in test_recipients:
        response = requests.post(
            f'{BASE_URL}/api/email/recipients',
            json=recipient
        )
        data = response.json()
        print(f"添加 {recipient['email_address']}: 状态码 {response.status_code}, {data.get('message', data.get('error', ''))}")
    
    # 3. 再次获取接收邮箱列表
    print("\n3. 再次获取接收邮箱列表")
    response = requests.get(f'{BASE_URL}/api/email/recipients')
    data = response.json()
    print(f"激活的接收邮箱数量: {len(data.get('data', []))}")
    for recipient in data.get('data', []):
        print(f"  - {recipient['email_address']} ({recipient['name']})")
    
    # 4. 测试更新接收邮箱
    print("\n4. 测试更新接收邮箱")
    if data.get('data'):
        recipient_id = data['data'][0]['id']
        response = requests.put(
            f'{BASE_URL}/api/email/recipients/{recipient_id}',
            json={'name': 'API更新后的姓名'}
        )
        data = response.json()
        print(f"更新接收邮箱ID {recipient_id}: 状态码 {response.status_code}, {data.get('message', data.get('error', ''))}")
    
    # 5. 测试切换激活状态
    print("\n5. 测试切换激活状态")
    if data.get('data'):
        recipient_id = data['data'][0]['id']
        response = requests.put(
            f'{BASE_URL}/api/email/recipients/{recipient_id}',
            json={'is_active': False}
        )
        data = response.json()
        print(f"禁用接收邮箱ID {recipient_id}: 状态码 {response.status_code}, {data.get('message', data.get('error', ''))}")
    
    # 6. 测试导出接收邮箱
    print("\n6. 测试导出接收邮箱")
    response = requests.get(f'{BASE_URL}/api/email/recipients/export')
    print(f"导出接收邮箱: 状态码 {response.status_code}")
    
    # 7. 清理测试数据
    print("\n7. 清理测试数据")
    response = requests.get(f'{BASE_URL}/api/email/recipients')
    data = response.json()
    for recipient in data.get('data', []):
        if recipient['email_address'].startswith('api_test'):
            response = requests.delete(f'{BASE_URL}/api/email/recipients/{recipient["id"]}')
            result_data = response.json()
            print(f"删除 {recipient['email_address']}: 状态码 {response.status_code}, {result_data.get('message', result_data.get('error', ''))}")
    
    print("\n" + "=" * 50)
    print("API测试完成")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_email_recipients_api()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"错误: {e}")