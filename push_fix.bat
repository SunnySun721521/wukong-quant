@echo off
chcp 65001 > nul
cd /d "D:\trae\备份悟空52224"

echo ========================================
echo Git Push Script
echo ========================================

echo.
echo [1/3] Adding all changes...
git add .

echo.
echo [2/3] Committing changes...
git commit -m "Fix Render: IndentationError in app.py"

echo.
echo [3/3] Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo Done!
echo ========================================
pause
