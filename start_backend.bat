@echo off

cd /d "%~dp0backend"
echo 正在启动后端服务器...
echo 服务器地址: http://localhost:5004
echo 按 Ctrl+C 停止服务器

echo.
python app.py
