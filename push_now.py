#!/usr/bin/env python3
import subprocess
import os

# Use current directory
project_dir = os.getcwd()
print(f"Current dir: {project_dir}")

# Git add
result = subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
print("Git add output:", result.stdout, result.stderr)

# Git commit
result = subprocess.run(
    ["git", "commit", "-m", "Fix prediction URL, data timeout, render compat"],
    capture_output=True, text=True,
    env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
)
print("Git commit output:", result.stdout, result.stderr)

# Git push
result = subprocess.run(
    ["git", "push", "origin", "main"],
    capture_output=True, text=True,
    env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    timeout=60
)
print("Git push output:", result.stdout, result.stderr)
