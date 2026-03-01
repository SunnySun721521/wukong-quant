import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
import pandas as pd
import io

print("=" * 50)
print("测试导入接收邮箱API")
print("=" * 50)

# 创建测试Excel文件
test_data = {
    'email_address': ['import_test1@example.com', 'import_test2@example.com'],
    'name': ['导入测试1', '导入测试2'],
    'description': ['导入测试邮箱1', '导入测试邮箱2']
}

df = pd.DataFrame(test_data)

# 保存到内存
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='接收邮箱列表')
buffer.seek(0)

# 使用Flask测试客户端
with app.app.test_client() as client:
    # 测试导入Excel文件
    print("\n1. 测试导入Excel文件")
    buffer.seek(0)
    response = client.post(
        '/api/email/recipients/import',
        data={'file': (buffer, 'test_import.xlsx')},
        content_type='multipart/form-data'
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.get_json()}")
    
    data = response.get_json()
    if data.get('success'):
        print(f"导入成功: {data.get('message')}")
        print(f"成功数量: {data.get('success_count')}")
        print(f"失败数量: {data.get('error_count')}")
        if data.get('errors'):
            print(f"错误详情: {data.get('errors')}")
    else:
        print(f"导入失败: {data.get('error')}")
    
    # 验证导入结果
    print("\n2. 验证导入结果")
    response = client.get('/api/email/recipients')
    data = response.get_json()
    recipients = data.get('data', [])
    print(f"当前接收邮箱数量: {len(recipients)}")
    for recipient in recipients:
        if 'import_test' in recipient['email_address']:
            print(f"  - {recipient['email_address']} ({recipient['name']})")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)