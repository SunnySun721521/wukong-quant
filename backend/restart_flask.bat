@echo off
echo 重启Flask应用...
echo 将确保应用重启间隔至少30秒，定时任务间隔至少5分钟

cd /d "%~dp0"

python restart_flask.py

pause