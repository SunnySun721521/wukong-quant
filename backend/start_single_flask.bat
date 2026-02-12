@echo off
echo 正在检查Flask应用实例...

cd /d "%~dp0"

REM 检查并确保只有一个Flask应用实例在运行
python ensure_single_instance.py

REM 根据检查结果决定是否启动新实例
python -c "import ensure_single_instance; need_start = ensure_single_instance.check_and_ensure_single_instance(); exit(0 if not need_start else 1)"

if %errorlevel% equ 1 (
    echo 启动新的Flask应用实例...
    start /B python app.py
) else (
    echo Flask应用实例已在运行，无需启动新实例
)

pause