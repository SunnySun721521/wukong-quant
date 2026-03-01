import subprocess
import os

os.chdir(r"D:\trae\备份悟空52224")

commands = [
    ["git", "add", "-A"],
    ["git", "commit", "-m", "Update all files"],
    ["git", "push", "-u", "origin", "main", "--force"]
]

for cmd in commands:
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    print(f"stdout: {result.stdout}")
    if result.stderr:
        print(f"stderr: {result.stderr}")
    print(f"returncode: {result.returncode}")
    print("---")

print("Done!")
