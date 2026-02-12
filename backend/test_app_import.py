import sys
import traceback

try:
    print("正在导入app模块...")
    import app
    print("app模块导入成功")
    
    print("正在检查Flask应用...")
    if hasattr(app, 'app'):
        print(f"Flask应用对象存在: {app.app}")
    else:
        print("Flask应用对象不存在")
    
    print("正在检查路由...")
    routes = [rule.rule for rule in app.app.url_map.iter_rules()]
    print(f"总路由数: {len(routes)}")
    
    email_routes = [r for r in routes if 'email' in r]
    print(f"邮件相关路由数: {len(email_routes)}")
    for route in email_routes:
        print(f"  - {route}")
    
    print("\n所有测试通过！")
    
except Exception as e:
    print(f"错误: {e}")
    traceback.print_exc()
    sys.exit(1)