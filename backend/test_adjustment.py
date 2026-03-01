# -*- coding: utf-8 -*-
import os
import sys

# 设置工作目录
os.chdir(r"D:\trae\备份悟空52224\backend")
sys.path.insert(0, r"D:\trae\备份悟空52224\backend")
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 测试导入
try:
    import app
    print("Import successful!")
    
    # 测试调仓策略 API
    with app.app.test_client() as client:
        response = client.get('/api/plan/adjustment')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.data.decode('utf-8')[:500]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
