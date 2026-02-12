import requests
import json

BASE_URL = 'http://127.0.0.1:5006'

def test_email_config():
    """测试邮件配置"""
    print("=" * 50)
    print("测试邮件配置")
    print("=" * 50)
    
    # 1. 测试获取邮件配置
    print("\n1. 测试获取邮件配置")
    response = requests.get(f'{BASE_URL}/api/email/config')
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"返回数据类型: {type(data)}")
    print(f"enabled值: {data.get('enabled')}")
    print(f"sender_email值: {data.get('sender_email')}")
    print(f"recipients值: {data.get('recipients')}")
    
    # 2. 测试保存邮件配置
    print("\n2. 测试保存邮件配置")
    config = {
        'enabled': True,
        'sender_email': '25285603@qq.com',
        'sender_auth_code': 'test_auth_code',
        'email_body_template': 'simple'
    }
    
    response = requests.post(
        f'{BASE_URL}/api/email/config',
        json=config
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {data}")
    
    # 3. 再次获取配置验证
    print("\n3. 再次获取配置验证")
    response = requests.get(f'{BASE_URL}/api/email/config')
    data = response.json()
    print(f"enabled值: {data.get('enabled')}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_email_config()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"错误: {e}")