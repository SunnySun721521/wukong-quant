@echo off
chcp 65001 > nul
cls
echo ========================================
echo 备份悟空52224 - 公网部署
echo ========================================
echo.

REM 检查应用是否运行
echo [检查] 本地应用状态...
netstat -ano | findstr ":5006" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ✓ 应用正在运行 (端口 5006)
) else (
    echo ✗ 应用未运行，正在启动...
    cd /d "%~dp0backend"
    start /B python app.py > app.log 2>&1
    timeout /t 3 /nobreak >nul
    echo ✓ 应用已启动
)

echo.
echo ========================================
echo 选择公网部署方案
echo ========================================
echo.
echo 1. serveo.net (推荐)
echo    - 完全免费，无需注册
echo    - 需要安装 SSH 客户端
echo.
echo 2. localtunnel (推荐)
echo    - 完全免费，无需注册
echo    - 需要安装 Node.js
echo.
echo 3. pyngrok (最简单)
echo    - Python 原生支持
echo    - 需要注册 ngrok 账号
echo.
echo 4. Cloudflare Tunnel (长期稳定)
echo    - 免费且稳定，支持自定义域名
echo    - 配置相对复杂
echo.
echo 5. 查看详细部署文档
echo.
echo 6. 退出
echo.
set /p choice="请输入选项 (1-6): "

if "%choice%"=="1" goto serveo
if "%choice%"=="2" goto localtunnel
if "%choice%"=="3" goto pyngrok
if "%choice%"=="4" goto cloudflare
if "%choice%"=="5" goto docs
if "%choice%"=="6" goto end

:serveo
echo.
echo ========================================
echo 启动 serveo.net 隧道
echo ========================================
echo.
python "%~dp0start_serveo.py"
goto end

:localtunnel
echo.
echo ========================================
echo 启动 localtunnel 隧道
echo ========================================
echo.
python "%~dp0start_localtunnel.py"
goto end

:pyngrok
echo.
echo ========================================
echo 启动 pyngrok 隧道
echo ========================================
echo.
python "%~dp0start_public_tunnel.py"
goto end

:cloudflare
echo.
echo ========================================
echo Cloudflare Tunnel 部署
echo ========================================
echo.
echo 请按照以下步骤操作：
echo.
echo 1. 运行配置脚本: setup_cloudflare_tunnel.bat
echo 2. 启动隧道: start_cloudflare_tunnel.bat
echo.
pause
goto end

:docs
echo.
echo ========================================
echo 打开部署文档
echo ========================================
echo.
start "" "%~dp0PUBLIC_DEPLOYMENT_GUIDE.md"
echo 已打开部署文档
echo.
pause
goto end

:end
echo.
echo ========================================
echo 感谢使用！
echo ========================================
pause