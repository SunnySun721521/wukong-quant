import sys
import os

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加路径
sys.path.insert(0, r'd:\trae\备份悟空52224\backend')

# 尝试导入
try:
    import app
    print("App imported successfully!")
    print("Flask app:", app.app)
    print("Routes:", [rule.rule for rule in app.app.url_map.iter_rules()])
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
