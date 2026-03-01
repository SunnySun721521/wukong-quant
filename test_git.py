# -*- coding: utf-8 -*-
import subprocess
import sys

print("Python路径:", sys.executable)
print()

# 测试git是否可用
result = subprocess.run(["git", "--version"], capture_output=True, text=True)
print("Git版本:", result.stdout.strip())
print("返回码:", result.returncode)

print("\n测试git status...")
result = subprocess.run(["git", "status"], capture_output=True, text=True, encoding='utf-8')
print(result.stdout)
if result.stderr:
    print("错误:", result.stderr)
