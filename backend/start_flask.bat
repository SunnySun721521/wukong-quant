@echo off
echo 正在启动Flask应用...

cd /d "%~dp0"

REM 使用单实例机制启动Flask应用
python single_instance_flask.py

pause