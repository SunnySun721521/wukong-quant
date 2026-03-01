#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import sys
import requests
import threading
import re

def check_local_app():
    """检查本地应用是否运行"""
    print("[1/3] 检查本地应用...")
    try:
        response = requests.get('http://127.0.0.1:5006/login.html', timeout=5)
        if response.status_code == 200:
            print("✓ 本地应用运行正常 (端口 5006)")
            return True
        else:
            print("✗ 本地应用响应异常")
            return False
    except Exception as e:
        print(f"✗ 本地应用未运行: {e}")
        print("请先启动应用: cd backend && python app.py")
        return False

def start_serveo():
    """启动 serveo.net 隧道"""
    print()
    print("[2/3] 启动 serveo.net 隧道...")
    print("正在连接 serveo.net 服务器，请稍候...")
    print()
    
    try:
        # 使用 ssh 连接 serveo.net
        # -R 参数: 远程端口转发
        # -o 参数: SSH 选项
        # ServerAliveInterval: 保持连接活跃
        process = subprocess.Popen(
            ['ssh', '-R', '80:localhost:5006', '-o', 'ServerAliveInterval=60', 'serveo.net'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True
        )
        
        # 读取输出
        def read_output():
            url_found = False
            while True:
                output = process.stderr.readline() if process.stderr else ""
                stdout_output = process.stdout.readline() if process.stdout else ""
                
                if output == '' and stdout_output == '' and process.poll() is not None:
                    break
                
                combined = (output + stdout_output).strip()
                if combined:
                    print(combined)
                    
                    # 检查是否包含 URL
                    if not url_found and ('serveo.net' in combined or 'Forwarding' in combined):
                        # 尝试提取 URL
                        url_match = re.search(r'https?://[a-zA-Z0-9.-]+\.serveo\.net', combined)
                        if url_match:
                            url = url_match.group(0)
                            url_found = True
                            print()
                            print("=" * 60)
                            print("公网访问地址")
                            print("=" * 60)
                            print()
                            print(f"🌐 {url}")
                            print()
                            print("=" * 60)
                            print("访问说明")
                            print("=" * 60)
                            print()
                            print("1. 复制上面的地址")
                            print("2. 在浏览器中打开")
                            print("3. 访问登录页面: /login.html")
                            print("4. 登录凭证:")
                            print("   用户名: admin")
                            print("   密码: libo0519")
                            print()
                            print("=" * 60)
                            print("重要提示")
                            print("=" * 60)
                            print()
                            print("✓ 免费且无需注册")
                            print("⚠️  地址每次重启都会变化")
                            print("⚠️  本窗口关闭后，隧道将停止")
                            print()
                            print("按 Ctrl+C 停止隧道")
                            print()
        
        # 启动读取线程
        output_thread = threading.Thread(target=read_output)
        output_thread.daemon = True
        output_thread.start()
        
        # 等待进程结束
        process.wait()
        
        print()
        print("[3/3] 隧道已停止")
        return True
        
    except FileNotFoundError:
        print("✗ SSH 客户端未找到")
        print()
        print("解决方案:")
        print("1. Windows: 启用 OpenSSH 客户端")
        print("   - 设置 > 应用 > 可选功能 > OpenSSH 客户端")
        print("2. 下载 PuTTY: https://www.putty.org/")
        return False
    except Exception as e:
        print(f"✗ 隧道启动失败: {e}")
        print()
        print("可能的原因:")
        print("1. serveo.net 服务暂时不可用")
        print("2. 网络连接问题")
        print("3. SSH 客户端未安装")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("备份悟空52224 - 公网部署 (serveo.net)")
    print("=" * 60)
    print()
    
    # 检查本地应用
    if not check_local_app():
        return 1
    
    # 启动隧道
    success = start_serveo()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())