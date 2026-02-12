@echo off
chcp 65001 > nul
echo ========================================
echo 启动 Cloudflare Tunnel
echo ========================================
echo.

REM 检查 cloudflared 是否已安装
where cloudflared >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ cloudflared 未安装
    echo 请先运行 setup_cloudflare_tunnel.bat 进行配置
    pause
    exit /b 1
)

REM 检查配置文件是否存在
if not exist "%~dp0cloudflared.yml" (
    echo ✗ 配置文件不存在
    echo 请先运行 setup_cloudflare_tunnel.bat 进行配置
    pause
    exit /b 1
)

REM 检查应用是否运行
echo [1/3] 检查应用状态...
netstat -ano | findstr ":5006" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ✓ 应用正在运行（端口5006）
) else (
    echo ✗ 应用未运行，正在启动...
    cd /d "%~dp0backend"
    start /B python app.py > app.log 2>&1
    timeout /t 3 /nobreak >nul
    echo ✓ 应用已启动
)

echo.
echo [2/3] 启动 Cloudflare Tunnel...
echo 正在启动 Tunnel，请稍候...
echo.
echo Tunnel 运行后，您可以通过配置的域名访问应用
echo 按 Ctrl+C 停止 Tunnel
echo.

REM 启动 Tunnel
cloudflared tunnel --config "%~dp0cloudflared.yml" run

echo.
echo [3/3] Tunnel 已停止
echo.
pause