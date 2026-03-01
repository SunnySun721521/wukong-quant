@echo off
chcp 65001 >nul
cd /d D:\trae\备份悟空52224

echo ========================================
echo Git 推送脚本
echo ========================================

echo.
echo [1/4] 检查 Git 状态...
git status

echo.
echo [2/4] 添加所有更改...
git add -A

echo.
echo [3/4] 提交更改...
git commit -m "feat: 添加 yfinance 数据源、修复邮件发送和 PDF 乱码问题

- Render 环境优先使用 yfinance 获取股票数据
- 修复自动发送邮件功能（初始化邮箱配置到数据库）
- 修复测试邮件功能
- 修复 PDF 导出中文乱码问题（自动下载中文字体）
- 创建统一数据库初始化模块 render_data_init.py
- 创建 Render 数据获取模块 render_data_provider.py"

echo.
echo [4/4] 推送到 GitHub...
git push origin main

echo.
echo ========================================
echo 推送完成！
echo ========================================
pause
