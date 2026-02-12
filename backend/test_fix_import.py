import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
import pandas as pd

print("=" * 50)
print("测试修复后的导入功能")
print("=" * 50)

# 使用Flask测试客户端
with app.app.test_client() as client:
    # 1. 清空所有接收邮箱
    print("\n1. 清空所有接收邮箱")
    response = client.delete('/api/email/recipients')
    data = response.get_json()
    print(f"清空结果: {data}")
    
    # 2. 读取用户的Excel文件
    print("\n2. 读取用户的Excel文件")
    file_path = r'C:\Users\Sunny Sun\Desktop\邮箱地址.xls'
    
    # 读取文件并清理列名
    df = pd.read_excel(file_path)
    print(f"原始列名: {list(df.columns)}")
    
    # 清理列名（去除前后空格）
    df.columns = df.columns.str.strip()
    print(f"清理后列名: {list(df.columns)}")
    
    # 3. 测试导入Excel文件
    print("\n3. 测试导入Excel文件")
    
    # 重新读取文件用于导入
    with open(file_path, 'rb') as f:
        from io import BytesIO
        buffer = BytesIO(f.read())
        buffer.seek(0)
        
        response = client.post(
            '/api/email/recipients/import',
            data={'file': (buffer, '邮箱地址.xls')},
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
    
    # 4. 验证导入结果
    print("\n4. 验证导入结果")
    response = client.get('/api/email/recipients')
    data = response.get_json()
    recipients = data.get('data', [])
    print(f"当前接收邮箱数量: {len(recipients)}")
    for recipient in recipients:
        print(f"  - {recipient['email_address']} ({recipient['name']}) - 激活: {recipient['is_active']}")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)