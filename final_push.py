import subprocess
import os
import sys

os.chdir(r"D:\trae\备份悟空52224")

print("Pushing to GitHub...")
proc = subprocess.Popen(
    ["git", "push", "origin", "main", "--force", "--progress"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8',
    errors='replace'
)

for line in proc.stdout:
    print(line, end='')

proc.wait()
print(f"\nExit code: {proc.returncode}")
