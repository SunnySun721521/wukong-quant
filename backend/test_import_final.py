import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
import pandas as pd
import io

print("=" * 50)
print("清理测试数据并重新测试导入")
print("=" * 50)

# 使用Flask测试客户端
with app.app.test_client() as client:
    # 1. 清空所有接收邮箱
    print("\n1. 清空所有接收邮箱")
    response = client.delete('/api/email/recipients')
    data = response.get_json()
    print(f"清空结果: {data}")
    
    # 2. 验证清空结果
    print("\n2. 验证清空结果")
    response = client.get('/api/email/recipients')
    data = response.get_json()
    recipients = data.get('data', [])
    print(f"当前接收邮箱数量: {len(recipients)}")
    
    # 3. 创建测试Excel文件
    print("\n3. 创建测试Excel文件")
    test_data = {
        'email_address': ['new_test1@example.com', 'new_test2@example.com', 'new_test3@example.com'],
        'name': ['新测试1', '新测试2', '新测试3'],
        'description': ['新测试邮箱1', '新测试邮箱2', '新测试邮箱3']
    }
    
    df = pd.DataFrame(test_data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='接收邮箱列表')
    buffer.seek(0)
    
    # 4. 测试导入Excel文件
    print("\n4. 测试导入Excel文件")
    buffer.seek(0)
    response = client.post(
        '/api/email/recipients/import',
        data={'file': (buffer, 'test_import.xlsx')},
        content_type='multipart/form-data'
    )
    
    print(f"状态码: {response.status_code}")
    data = response.get_json()
    print(f"响应内容: {data}")
    
    if data.get('success'):
        print(f"导入成功: {data.get('message')}")
        print(f"成功数量: {data.get('success_count')}")
        print(f"失败数量: {data.get('error_count')}")
        if data.get('errors'):
            print(f"错误详情: {data.get('errors')}")
    else:
        print(f"导入失败: {data.get('error')}")
    
    # 5. 验证导入结果
    print("\n5. 验证导入结果")
    response = client.get('/api/email/recipients')
    data = response.get_json()
    recipients = data.get('data', [])
    print(f"当前接收邮箱数量: {len(recipients)}")
    for recipient in recipients:
        print(f"  - {recipient['email_address']} ({recipient['name']}) - 激活: {recipient['is_active']}")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)