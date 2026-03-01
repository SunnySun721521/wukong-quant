# -*- coding: utf-8 -*-
import os
import sys

# 设置工作目录
os.chdir(r"D:\trae\备份悟空52224\backend")
sys.path.insert(0, r"D:\trae\备份悟空52224\backend")

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 导入并运行原始 app
import app

if __name__ == '__main__':
    print("Starting original app.py on port 5006...")
    app.app.run(host='0.0.0.0', port=5006, debug=False, use_reloader=False)
