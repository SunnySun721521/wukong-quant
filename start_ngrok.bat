@echo off
chcp 65001 > nul
echo ========================================
echo 备份悟空52224 - ngrok公网部署
echo ========================================
echo.

REM 检查ngrok是否已安装
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ ngrok未安装或未添加到PATH
    echo.
    echo 请按以下步骤安装ngrok：
    echo 1. 访问 https://ngrok.com/download
    echo 2. 下载Windows版本
    echo 3. 解压到任意目录
    echo 4. 将ngrok.exe所在目录添加到系统PATH
    echo 5. 或者将ngrok.exe复制到当前目录
    echo.
    pause
    exit /b 1
)

echo ✓ ngrok已安装
echo.

REM 检查应用是否运行
echo [1/4] 检查应用状态...
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
echo [2/4] 检查ngrok配置...
if exist "%~dp0ngrok.yml" (
    echo ✓ 找到ngrok配置文件
) else (
    echo ✗ 未找到ngrok配置文件，使用默认配置
)

echo.
echo [3/4] 启动ngrok...
echo 正在启动ngrok，请稍候...
echo.

REM 启动ngrok
ngrok http 5006

echo.
echo [4/4] 部署完成
echo ========================================
echo.
echo 如果ngrok成功启动，您会看到类似以下信息：
echo.
echo Forwarding  https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:5006
echo.
echo 使用上面的https地址即可从公网访问您的应用
echo.
echo 注意：
echo - 免费版ngrok地址每次重启都会变化
echo - 建议升级到付费版以获得固定域名
echo - 生产环境建议使用云服务器部署
echo.
pause