# -*- coding: utf-8 -*-
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("正在启动服务器...")
print(f"工作目录: {os.getcwd()}")

try:
    from app import run_app
    run_app()
except Exception as e:
    print(f"启动失败: {e}")
    import traceback
    traceback.print_exc()
    input("按回车键退出...")
