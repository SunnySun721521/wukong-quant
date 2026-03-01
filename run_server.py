import subprocess
import os
import sys

# 设置环境变量
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

# 切换目录
os.chdir(r"d:\trae\备份悟空52224\backend")

# 启动服务器
print("Starting server...")
process = subprocess.Popen(
    [sys.executable, "app.py"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# 读取输出
try:
    for line in process.stdout:
        print(line, end='')
except KeyboardInterrupt:
    process.terminate()
    process.wait()
