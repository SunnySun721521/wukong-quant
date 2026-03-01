import subprocess
import os
import sys

os.chdir(r"d:\trae\备份悟空52224\backend")
print("Starting Flask server...")
result = subprocess.run([sys.executable, "app.py"], capture_output=True, text=True, timeout=300)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
