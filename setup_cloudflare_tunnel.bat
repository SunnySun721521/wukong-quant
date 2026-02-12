@echo off
chcp 65001 > nul
echo ========================================
echo Cloudflare Tunnel 一键部署脚本
echo ========================================
echo.

REM 检查 cloudflared 是否已安装
where cloudflared >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ cloudflared 未安装
    echo.
    echo 请按以下步骤安装：
    echo 1. 访问：https://github.com/cloudflare/cloudflared/releases/latest
    echo 2. 下载 Windows 版本：cloudflared-windows-amd64.exe
    echo 3. 重命名为 cloudflared.exe
    echo 4. 放到系统 PATH 或当前目录
    echo.
    pause
    exit /b 1
)

echo ✓ cloudflared 已安装
echo.

REM 检查应用是否运行
echo [1/5] 检查应用状态...
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
echo [2/5] 登录 Cloudflare...
echo 如果浏览器未自动打开，请手动访问授权页面
echo.
cloudflared tunnel login

echo.
echo [3/5] 创建 Tunnel...
set /p TUNNEL_NAME="请输入 Tunnel 名称（默认: backup-wukong）: "
if "%TUNNEL_NAME%"=="" set TUNNEL_NAME=backup-wukong

cloudflared tunnel create %TUNNEL_NAME%

echo.
echo [4/5] 配置 DNS...
set /p DOMAIN="请输入域名（例如: wukong.yourdomain.com）: "

cloudflared tunnel route dns %TUNNEL_NAME% %DOMAIN%

echo.
echo [5/5] 创建配置文件...
for /f "tokens=2" %%i in ('cloudflared tunnel list ^| findstr %TUNNEL_NAME%') do set TUNNEL_ID=%%i

(
echo tunnel: %TUNNEL_ID%
echo credentials-file: ./cloudflared-%TUNNEL_ID%.json
echo.
echo ingress:
echo   - hostname: %DOMAIN%
echo     service: http://localhost:5006
echo   - service: http_status:404
) > cloudflared.yml

echo ✓ 配置文件已创建: cloudflared.yml

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 下一步：
echo 1. 运行以下命令启动 Tunnel：
echo    cloudflared tunnel run %TUNNEL_NAME%
echo.
echo 2. 或者使用配置文件运行：
echo    cloudflared tunnel --config cloudflared.yml run
echo.
echo 3. 访问您的应用：
echo    https://%DOMAIN%
echo.
echo 4. 如需作为 Windows 服务运行：
echo    cloudflared service install
echo    cloudflared service start
echo.
pause