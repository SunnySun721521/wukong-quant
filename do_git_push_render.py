# -*- coding: utf-8 -*-
"""
Git 推送脚本
用于将修改推送到 GitHub
"""
import subprocess
import os
import sys

def run_command(cmd, cwd=None):
    """运行命令并返回输出"""
    print(f"执行: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败: {e}")
        return False

def main():
    base_dir = r"D:\trae\备份悟空52224"
    
    print("=" * 50)
    print("Git 推送脚本")
    print("=" * 50)
    
    # 1. 检查状态
    print("\n[1/4] 检查 Git 状态...")
    run_command("git status", cwd=base_dir)
    
    # 2. 添加所有更改
    print("\n[2/4] 添加所有更改...")
    run_command("git add -A", cwd=base_dir)
    
    # 3. 提交更改
    print("\n[3/4] 提交更改...")
    commit_msg = """feat: 添加 yfinance 数据源、修复邮件发送和 PDF 乱码问题

- Render 环境优先使用 yfinance 获取股票数据
- 修复自动发送邮件功能（初始化邮箱配置到数据库）
- 修复测试邮件功能
- 修复 PDF 导出中文乱码问题（自动下载中文字体）
- 创建统一数据库初始化模块 render_data_init.py
- 创建 Render 数据获取模块 render_data_provider.py"""
    
    run_command(f'git commit -m "{commit_msg}"', cwd=base_dir)
    
    # 4. 推送到 GitHub
    print("\n[4/4] 推送到 GitHub...")
    success = run_command("git push origin main", cwd=base_dir)
    
    print("\n" + "=" * 50)
    if success:
        print("推送成功！")
    else:
        print("推送可能失败，请检查上方输出")
    print("=" * 50)
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
