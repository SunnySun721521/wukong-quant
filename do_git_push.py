import subprocess
import os

os.chdir(r"d:\trae\备份悟空52224")

print("=== 开始推送代码 ===")

# Git add
print("\n[1/3] git add -A")
r1 = subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
print("stdout:", r1.stdout)
print("stderr:", r1.stderr)

# Git commit
print("\n[2/3] git commit")
r2 = subprocess.run(["git", "commit", "-m", "Fix prediction URL and data timeout"], capture_output=True, text=True)
print("stdout:", r2.stdout)
print("stderr:", r2.stderr)

# Git push
print("\n[3/3] git push")
r3 = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, timeout=120)
print("stdout:", r3.stdout)
print("stderr:", r3.stderr)

print("\n=== 完成 ===")
