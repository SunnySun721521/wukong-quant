#!/usr/bin/env python3
import subprocess
import os

os.chdir(r"d:\trae\备份悟空52224")

# Add all changes
result = subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
print(result.stdout)

# Commit
result = subprocess.run(
    ["git", "commit", "-m", "Fix: prediction API URL, data_provider timeout, render_compat"],
    capture_output=True, text=True,
    env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
)
print(result.stdout)

# Push
result = subprocess.run(
    ["git", "push", "origin", "main"],
    capture_output=True, text=True,
    env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
)
print(result.stdout)
print(result.stderr)
