@echo off
chcp 65001 >nul
echo ========================================
echo 正在推送代码到 GitHub...
echo ========================================
echo.

cd /d "d:\trae\备份悟空52224"

echo [1/3] 添加文件...
git add -A
if %errorlevel% neq 0 (
    echo 添加文件失败！
    pause
    exit /b 1
)

echo [2/3] 提交更改...
git commit -m "Fix prediction URL, data timeout, render compat"
if %errorlevel% neq 0 (
    echo 提交失败或没有更改需要提交
)

echo [3/3] 推送到 GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo 推送失败！可能需要输入 GitHub 凭据
    echo 请尝试手动执行: git push origin main
)

echo.
echo ========================================
echo 完成！
echo ========================================
pause
