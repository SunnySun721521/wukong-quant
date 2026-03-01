@echo off

REM 启动本地Web服务器
REM 使用Python的内置http.server模块

cd /d "%~dp0"
echo 正在启动Web服务器...
echo 服务器地址: http://localhost:8000
echo 按 Ctrl+C 停止服务器

echo.
python -m http.server 8000
