import os
import sys
import subprocess

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 切换目录
os.chdir(r"d:\trae\备份悟空52224\backend")

# 使用 subprocess 运行 app.py
result = subprocess.run(
    [sys.executable, "app.py"],
    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
    capture_output=True,
    text=True
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
