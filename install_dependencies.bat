@echo off
chcp 65001 >nul
echo ========================================
echo    量化交易系统 - 依赖安装
echo ========================================
echo.
echo 正在安装Python依赖包...
echo.
pip install -r requirements.txt
echo.
echo ========================================
echo    依赖安装完成！
echo ========================================
pause