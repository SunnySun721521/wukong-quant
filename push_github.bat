@echo off
chcp 65001 >nul
echo ========================================
echo 推送代码到 GitHub
echo ========================================
echo.

cd /d "d:\trae\备份悟空52224"
echo 当前目录: %CD%
echo.

echo [1/3] 检查 Git 状态...
git status
echo.

echo [2/3] 推送到 GitHub...
git push origin main --force
if %errorlevel% neq 0 (
    echo.
    echo 推送失败！尝试使用其他方法...
    echo.
    echo 方法 1: 重新设置上游分支
    git branch --unset-upstream
    git push -u origin main
    if %errorlevel% neq 0 (
        echo.
        echo 方法 2: 强制推送所有分支
        git push origin --all --force
    )
)

echo.
echo ========================================
echo 完成！
echo ========================================
pause
