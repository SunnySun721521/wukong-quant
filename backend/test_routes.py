import requests

BASE_URL = 'http://127.0.0.1:5006'

# 测试导入路由
print("测试导入路由...")
response = requests.get(f'{BASE_URL}/api/email/recipients/import')
print(f"GET /api/email/recipients/import: {response.status_code}")
print(f"响应: {response.text}")

# 测试导出路由
print("\n测试导出路由...")
response = requests.get(f'{BASE_URL}/api/email/recipients/export')
print(f"GET /api/email/recipients/export: {response.status_code}")
print(f"响应: {response.text}")

# 测试获取接收邮箱列表
print("\n测试获取接收邮箱列表...")
response = requests.get(f'{BASE_URL}/api/email/recipients')
print(f"GET /api/email/recipients: {response.status_code}")
print(f"响应: {response.text}")