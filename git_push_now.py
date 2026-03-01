# -*- coding: utf-8 -*-
import subprocess
import os
import sys

def run_git():
    os.chdir(r"D:\trae\备份悟空52224")
    
    print("当前目录:", os.getcwd())
    print("Python:", sys.executable)
    
    commands = [
        ["git", "status"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Fix Render: IndentationError in app.py"],
        ["git", "push", "origin", "main"]
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n[{i}/4] 执行: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=60)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            print(f"返回码: {result.returncode}")
        except Exception as e:
            print(f"错误: {e}")
    
    print("\n完成!")

if __name__ == "__main__":
    run_git()
