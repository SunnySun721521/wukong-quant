@echo off
chcp 65001 > nul
echo ========================================
echo 备份悟空52224 - 公网部署脚本
echo ========================================
echo.

echo [1/4] 检查应用状态...
tasklist /FI "IMAGENAME eq python.exe" | findstr python.exe >nul
if %errorlevel% equ 0 (
    echo ✓ Python应用正在运行
) else (
    echo ✗ Python应用未运行，正在启动...
    cd /d "%~dp0backend"
    start /B python app.py > app.log 2>&1
    timeout /t 3 /nobreak >nul
    echo ✓ 应用已启动
)

echo.
echo [2/4] 检查端口5006...
netstat -ano | findstr ":5006" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ✓ 端口5006正在监听
) else (
    echo ✗ 端口5006未监听，请检查应用状态
    pause
    exit /b 1
)

echo.
echo [3/4] 获取本地IP地址...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    set LOCAL_IP=%%a
    set LOCAL_IP=!LOCAL_IP: =!
)
echo ✓ 本地IP: !LOCAL_IP!
echo ✓ 本地访问地址: http://127.0.0.1:5006
echo ✓ 局域网访问地址: http://!LOCAL_IP!:5006

echo.
echo [4/4] 公网部署方案
echo ========================================
echo 请选择公网部署方案：
echo.
echo 1. 使用ngrok（推荐，最简单快速）
echo    - 需要下载ngrok: https://ngrok.com/download
echo    - 注册账号获取authtoken
echo    - 免费版提供临时公网地址
echo.
echo 2. 使用frp（稳定可靠）
echo    - 需要一台有公网IP的服务器
echo    - 配置相对复杂，但更稳定
echo.
echo 3. 使用云服务器（生产环境推荐）
echo    - 购买云服务器（阿里云、腾讯云等）
echo    - 部署到云服务器，稳定性和安全性最好
echo.
echo 4. 查看详细部署文档
echo.
set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" goto ngrok
if "%choice%"=="2" goto frp
if "%choice%"=="3" goto cloud
if "%choice%"=="4" goto docs

:ngrok
echo.
echo ========================================
echo 使用ngrok进行公网部署
echo ========================================
echo.
echo 步骤1: 下载ngrok
echo 访问: https://ngrok.com/download
echo 下载Windows版本并解压
echo.
echo 步骤2: 注册账号
echo 访问: https://dashboard.ngrok.com/signup
echo 注册账号并获取authtoken
echo.
echo 步骤3: 配置ngrok
echo 运行命令: ngrok config add-authtoken YOUR_AUTHTOKEN
echo.
echo 步骤4: 启动ngrok
echo 运行命令: ngrok http 5006
echo.
echo 步骤5: 获取公网地址
echo ngrok会显示一个临时公网地址
echo 使用该地址访问应用
echo.
pause
exit /b 0

:frp
echo.
echo ========================================
echo 使用frp进行公网部署
echo ========================================
echo.
echo 需要准备：
echo 1. 一台有公网IP的服务器
echo 2. 下载frp: https://github.com/fatedier/frp/releases
echo.
echo 配置步骤：
echo 1. 在服务器上配置frps.ini
echo 2. 在本地配置frpc.ini
echo 3. 启动frpc客户端
echo.
pause
exit /b 0

:cloud
echo.
echo ========================================
echo 使用云服务器部署
echo ========================================
echo.
echo 推荐云服务商：
echo 1. 阿里云: https://www.aliyun.com
echo 2. 腾讯云: https://cloud.tencent.com
echo 3. 华为云: https://www.huaweicloud.com
echo.
echo 部署步骤：
echo 1. 购买云服务器
echo 2. 安装Python环境
echo 3. 上传项目文件
echo 4. 配置防火墙（开放5006端口）
echo 5. 使用Gunicorn或systemd运行应用
echo 6. 配置Nginx反向代理（可选）
echo.
pause
exit /b 0

:docs
echo.
echo ========================================
echo 打开部署文档
echo ========================================
echo.
start "" "%~dp0DEPLOYMENT.md"
echo 已打开部署文档
echo.
pause
exit /b 0