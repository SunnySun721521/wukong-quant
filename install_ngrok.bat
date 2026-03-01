@echo off
chcp 65001 > nul
echo ========================================
echo 下载和安装 ngrok
echo ========================================
echo.

set NGROK_URL=https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip
set NGROK_ZIP=ngrok.zip
set NGROK_DIR=%USERPROFILE%\ngrok

echo [1/4] 下载 ngrok...
echo 正在从 %NGROK_URL% 下载...
echo.

REM 使用 PowerShell 下载
powershell -Command "& {Invoke-WebRequest -Uri '%NGROK_URL%' -OutFile '%NGROK_ZIP%'}"

if %errorlevel% neq 0 (
    echo ✗ 下载失败
    echo 请手动下载：
    echo 1. 访问：https://ngrok.com/download
    echo 2. 下载 Windows 版本
    echo 3. 解压到任意目录
    pause
    exit /b 1
)

echo ✓ 下载成功
echo.

echo [2/4] 解压文件...
if not exist "%NGROK_DIR%" mkdir "%NGROK_DIR%"
powershell -Command "& {Expand-Archive -Path '%NGROK_ZIP%' -DestinationPath '%NGROK_DIR%' -Force}"

if %errorlevel% neq 0 (
    echo ✗ 解压失败
    pause
    exit /b 1
)

echo ✓ 解压成功
echo.

echo [3/4] 添加到系统 PATH...
setx PATH "%PATH%;%NGROK_DIR%" >nul

if %errorlevel% neq 0 (
    echo ⚠️  添加到 PATH 失败，但可以继续使用
) else (
    echo ✓ 已添加到系统 PATH
)

echo.
echo [4/4] 验证安装...
"%NGROK_DIR%\ngrok.exe" version

if %errorlevel% neq 0 (
    echo ✗ 验证失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo ngrok 已安装到：%NGROK_DIR%
echo.
echo 下一步：
echo 1. 访问：https://dashboard.ngrok.com/signup
echo 2. 注册账号
echo 3. 获取 authtoken
echo 4. 运行："%NGROK_DIR%\ngrok.exe" config add-authtoken YOUR_AUTHTOKEN
echo 5. 运行："%NGROK_DIR%\ngrok.exe" http 5006
echo.
pause