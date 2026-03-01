@echo off
chcp 65001 > nul
echo ========================================
echo 备份悟空52224 - 公网部署指南
echo ========================================
echo.
echo 当前状态：
echo - 本地应用: 运行中 (端口 5006)
echo - 局域网访问: http://172.168.1.58:5006
echo.
echo ========================================
echo 公网部署方案
echo ========================================
echo.
echo 方案1: 使用 pyngrok (Python)
echo   - 已安装 pyngrok
echo   - 运行: python start_public_tunnel.py
echo   - 优点: 简单快速
echo   - 缺点: 免费版地址会变化
echo.
echo 方案2: 使用 Cloudflare Tunnel
echo   - 需要注册 Cloudflare 账号
echo   - 运行: setup_cloudflare_tunnel.bat
echo   - 优点: 免费且稳定
echo   - 缺点: 配置相对复杂
echo.
echo 方案3: 使用 ngrok 命令行工具
echo   - 需要下载 ngrok
echo   - 访问: https://ngrok.com/download
echo   - 优点: 功能强大
echo   - 缺点: 需要注册
echo.
echo ========================================
echo 推荐方案
echo ========================================
echo.
echo 如果您想快速测试，推荐使用方案1 (pyngrok)
echo 如果您需要长期稳定访问，推荐使用方案2 (Cloudflare)
echo.
pause