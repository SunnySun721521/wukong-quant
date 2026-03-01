import subprocess
import os

os.chdir(r"d:\trae\备份悟空52224")

# Stage all files
subprocess.run(["git", "add", "-A"], check=True)

# Commit
result = subprocess.run(
    ["git", "commit", "-m", "Fix Render deployment: port env, render_compat init, PDF fonts, baostock timeout"],
    capture_output=True,
    text=True
)
print(result.stdout)
print(result.stderr)

# Push
result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
