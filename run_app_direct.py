# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r"D:\trae\备份悟空52224\backend")

# 使用系统Python运行app.py
result = subprocess.run(
    ["python", "app.py"],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='ignore'
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
