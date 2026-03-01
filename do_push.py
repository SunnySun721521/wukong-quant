import subprocess
import os

os.chdir(r"D:\trae")

env = os.environ.copy()
env['GIT_INDEX_FILE'] = r"D:\trae\备份悟空52224\.git\index"

commands = [
    ["git", "add", "备份悟空52224/backend/app.py", "备份悟空52224/web/plan.html", "备份悟空52224/web/backtest.html", "备份悟空52224/web/settings.html", "备份悟空52224/strategy/"],
    ["git", "commit", "-m", "Update"],
    ["git", "push", "origin", "main"]
]

for cmd in commands:
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env)
    print(f"stdout: {result.stdout}")
    if result.stderr:
        print(f"stderr: {result.stderr}")
    print(f"returncode: {result.returncode}")
    print("---")
