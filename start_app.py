import subprocess
import sys
import os
import time

os.chdir(r"d:\trae\备份悟空52224\backend")

process = subprocess.Popen(
    [sys.executable, "app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    bufsize=1,
    encoding='utf-8',
    errors='replace'
)

print("服务器启动中...")
time.sleep(5)

for line in process.stdout:
    print(line, end='')
    if "Running on" in line:
        print("\n服务器启动成功！")
        break
