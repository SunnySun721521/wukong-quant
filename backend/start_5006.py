# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time

os.chdir(r"D:\trae\备份悟空52224\backend")
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

print("Starting app.py on port 5006...")
process = subprocess.Popen(
    [sys.executable, "app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env=env,
    bufsize=1
)

try:
    for line in iter(process.stdout.readline, b''):
        try:
            decoded = line.decode('utf-8')
        except:
            decoded = line.decode('gbk', errors='ignore')
        print(decoded, end='')
        
        if "Running on" in decoded:
            print("Server started successfully!")
            time.sleep(2)
            break
except KeyboardInterrupt:
    print("\nStopped by user")
    process.terminate()
    process.wait()
