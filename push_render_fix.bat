@echo off
chcp 65001 > nul
cd /d "D:\trae\备份悟空52224"

echo ========================================
echo Git Push - Render Fixes
echo ========================================

echo.
echo [1/3] Adding all changes...
git add .

echo.
echo [2/3] Committing changes...
git commit -m "Fix Render: PDF Chinese fonts, backtest data, stock names, home page prices"

echo.
echo [3/3] Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo Done! Check Render dashboard for deployment.
echo ========================================
pause
