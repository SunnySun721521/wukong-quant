import requests
import pandas as pd
import io

BASE_URL = 'http://127.0.0.1:5006'

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

print("=" * 50)
print("测试导入接收邮箱API")
print("=" * 50)

# 测试导入Excel文件
print("\n1. 测试导入Excel文件")
files = {'file': ('test_import.xlsx', buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}

try:
    response = requests.post(
        f'{BASE_URL}/api/email/recipients/import',
        files=files
    )
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
    
    data = response.json()
    if data.get('success'):
        print(f"导入成功: {data.get('message')}")
        print(f"成功数量: {data.get('success_count')}")
        print(f"失败数量: {data.get('error_count')}")
        if data.get('errors'):
            print(f"错误详情: {data.get('errors')}")
    else:
        print(f"导入失败: {data.get('error')}")
except Exception as e:
    print(f"请求失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)