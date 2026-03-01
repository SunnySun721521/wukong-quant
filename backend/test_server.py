# -*- coding: utf-8 -*-
import os
import sys
os.chdir(r"D:\trae\备份悟空52224\backend")
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("开始启动...")
print("Python路径:", sys.executable)

try:
    from app import app
    print("Flask app loaded")
    print("路由数量:", len(app.url_map._rules))
    
    for rule in app.url_map.iter_rules():
        if 'backtestpool' in str(rule):
            print(f"  {rule} -> {rule.endpoint}")
    
    print("\n启动服务器...")
    app.run(host='0.0.0.0', port=5006, debug=False, threaded=True)
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
