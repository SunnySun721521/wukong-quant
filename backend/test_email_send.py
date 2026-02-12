import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app

print("=" * 50)
print("测试邮件发送")
print("=" * 50)

with app.app.test_client() as client:
    print("\n发送测试邮件:")
    response = client.post('/api/email/test', 
                        json={'recipients': ['lib@tcscd.com']},
                        content_type='application/json')
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.get_json()
        print(f"  响应: {data}")
    else:
        print(f"  请求失败")
        error_data = response.get_json()
        if error_data:
            print(f"  错误信息: {error_data}")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)