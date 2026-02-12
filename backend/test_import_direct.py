import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试导入API函数
print("测试导入API函数...")

# 检查app模块
try:
    import app
    print("✓ app模块导入成功")
except Exception as e:
    print(f"✗ app模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 检查Flask应用
try:
    flask_app = app.app
    print("✓ Flask应用获取成功")
except Exception as e:
    print(f"✗ Flask应用获取失败: {e}")

# 检查路由
try:
    with flask_app.test_client() as client:
        # 测试获取接收邮箱列表
        response = client.get('/api/email/recipients')
        print(f"✓ GET /api/email/recipients: {response.status_code}")
        
        # 测试导入路由
        response = client.get('/api/email/recipients/import')
        print(f"✓ GET /api/email/recipients/import: {response.status_code}")
        
        # 测试导出路由
        response = client.get('/api/email/recipients/export')
        print(f"✓ GET /api/email/recipients/export: {response.status_code}")
except Exception as e:
    print(f"✗ 测试路由失败: {e}")
    import traceback
    traceback.print_exc()