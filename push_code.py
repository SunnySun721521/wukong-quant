import subprocess
import os

os.chdir(r"d:\trae\备份悟空52224")
print(f"当前目录: {os.getcwd()}")

print("\n=== 开始推送代码 ===")

env = os.environ.copy()
env["GIT_TERMINAL_PROMPT"] = "0"

print("\n[1/3] git add -A")
r1 = subprocess.run(["git", "add", "-A"], capture_output=True, text=True, env=env)
print(f"返回码: {r1.returncode}")
if r1.stdout: print(f"输出: {r1.stdout}")
if r1.stderr: print(f"错误: {r1.stderr}")

print("\n[2/3] git commit")
r2 = subprocess.run(["git", "commit", "-m", "Fix prediction URL and improve Render compatibility"], capture_output=True, text=True, env=env)
print(f"返回码: {r2.returncode}")
if r2.stdout: print(f"输出: {r2.stdout}")
if r2.stderr: print(f"错误: {r2.stderr}")

print("\n[3/3] git push origin main")
r3 = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, env=env, timeout=120)
print(f"返回码: {r3.returncode}")
if r3.stdout: print(f"输出: {r3.stdout}")
if r3.stderr: print(f"错误: {r3.stderr}")

print("\n=== 完成 ===")
