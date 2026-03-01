# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time

# 切换到正确的目录
os.chdir(r"D:\trae\备份悟空52224\backend")

# 设置环境变量
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

# 启动进程
print("正在启动服务器...")
process = subprocess.Popen(
    [sys.executable, "app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env=env,
    bufsize=1
)

# 读取输出，使用 UTF-8 解码
try:
    for line in iter(process.stdout.readline, b''):
        try:
            print(line.decode('utf-8'), end='')
        except UnicodeDecodeError:
            print(line.decode('gbk', errors='ignore'), end='')
        if "Running on" in line.decode('utf-8', errors='ignore'):
            print("服务器启动成功！")
            break
except KeyboardInterrupt:
    print("\n用户中断")
    process.terminate()
    process.wait()
