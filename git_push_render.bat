@echo off
chcp 65001 > nul
cd /d "D:\trae\备份悟空52224"

echo ========================================
echo Git Push Script for Render Deployment
echo ========================================

echo.
echo [1/4] Checking git status...
git status

echo.
echo [2/4] Adding all changes...
git add .

echo.
echo [3/4] Committing changes...
git commit -m "Fix Render: PDF fonts, market status, backtest data, email sending"

echo.
echo [4/4] Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo Done! Please check Render dashboard for deployment status.
echo ========================================
pause
