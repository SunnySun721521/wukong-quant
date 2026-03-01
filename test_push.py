#!/usr/bin/env python3
import subprocess
import os
import time

os.chdir(r"d:\trae\备份悟空52224")

print("=== Testing git push ===")

# Try with verbose output
result = subprocess.run(
    ["git", "push", "-u", "origin", "main", "--verbose"],
    capture_output=True,
    text=True,
    timeout=60,
    env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
)
print("STDOUT:", result.stdout[:2000] if result.stdout else "Empty")
print("STDERR:", result.stderr[:2000] if result.stderr else "Empty")
print("Return code:", result.returncode)

# Check if there's a username/password prompt issue
if "authentication" in result.stderr.lower() or "credential" in result.stderr.lower():
    print("=== GitHub Authentication Issue ===")
    print("You may need to use a Personal Access Token (PAT) as password")
