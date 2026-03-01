# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r"D:\trae\备份悟空52224")

print("当前目录:", os.getcwd())

print("\n[1/4] Git Status...")
result = subprocess.run(["git", "status"], capture_output=True, text=True, encoding='utf-8')
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n[2/4] Git Add...")
result = subprocess.run(["git", "add", "."], capture_output=True, text=True, encoding='utf-8')
print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n[3/4] Git Commit...")
result = subprocess.run(["git", "commit", "-m", "Fix Render: IndentationError in app.py"], capture_output=True, text=True, encoding='utf-8')
print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n[4/4] Git Push...")
result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, encoding='utf-8')
print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n完成!")
input("按回车键退出...")
