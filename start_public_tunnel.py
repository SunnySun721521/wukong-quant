#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyngrok import ngrok
import time
import sys

def start_public_tunnel():
    """启动公网隧道"""
    print("=" * 60)
    print("备份悟空52224 - 公网部署")
    print("=" * 60)
    print()
    
    # 检查本地应用是否运行
    print("[1/3] 检查本地应用...")
    try:
        import requests
        response = requests.get('http://127.0.0.1:5006/login.html', timeout=5)
        if response.status_code == 200:
            print("✓ 本地应用运行正常 (端口 5006)")
        else:
            print("✗ 本地应用响应异常")
            return False
    except Exception as e:
        print(f"✗ 本地应用未运行: {e}")
        print("请先启动应用: cd backend && python app.py")
        return False
    
    print()
    print("[2/3] 启动 ngrok 隧道...")
    print("正在连接 ngrok 服务器，请稍候...")
    print()
    
    try:
        # 启动 ngrok 隧道
        public_url = ngrok.connect(5006, bind_tls=True)
        
        print("✓ 隧道启动成功！")
        print()
        print("=" * 60)
        print("公网访问地址")
        print("=" * 60)
        print()
        print(f"🌐 HTTPS: {public_url}")
        print(f"🌐 HTTP:  {public_url.replace('https://', 'http://')}")
        print()
        print("=" * 60)
        print("访问说明")
        print("=" * 60)
        print()
        print("1. 复制上面的 HTTPS 地址")
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
        print("⚠️  免费版 ngrok 地址每次重启都会变化")
        print("⚠️  如需固定域名，请升级到付费版")
        print("⚠️  本窗口关闭后，隧道将停止")
        print()
        print("按 Ctrl+C 停止隧道")
        print()
        
        # 保持隧道运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            print()
            print("[3/3] 正在停止隧道...")
            ngrok.disconnect(public_url)
            print("✓ 隧道已停止")
            return True
            
    except Exception as e:
        print(f"✗ 隧道启动失败: {e}")
        print()
        print("可能的原因:")
        print("1. ngrok 服务暂时不可用")
        print("2. 网络连接问题")
        print("3. ngrok 账号未配置")
        print()
        print("解决方案:")
        print("1. 检查网络连接")
        print("2. 访问 https://ngrok.com 注册账号")
        print("3. 配置 authtoken: ngrok config add-authtoken YOUR_TOKEN")
        return False

if __name__ == "__main__":
    success = start_public_tunnel()
    sys.exit(0 if success else 1)