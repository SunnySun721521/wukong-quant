import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app

print("检查邮件相关路由:")
routes = [rule.rule for rule in app.app.url_map.iter_rules()]
import_routes = [r for r in routes if 'import' in r]

print(f"包含'import'的路由: {import_routes}")

print("\n所有接收邮箱相关路由:")
recipient_routes = [r for r in routes if 'recipients' in r]
for route in recipient_routes:
    print(f"  - {route}")