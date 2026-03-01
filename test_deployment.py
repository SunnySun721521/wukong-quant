#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5006"

def test_connection():
    """测试连接"""
    print("=" * 60)
    print("1. 测试服务器连接")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/login.html", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器连接成功")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_login():
    """测试登录功能"""
    print("\n" + "=" * 60)
    print("2. 测试登录功能")
    print("=" * 60)
    
    data = {
        "username": "admin",
        "password": "libo0519"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=data, timeout=5)
        result = response.json()
        
        if result.get('success'):
            print("✅ 登录成功")
            print(f"   用户名: {result.get('username')}")
            return True
        else:
            print(f"❌ 登录失败: {result.get('message')}")
            return False
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")
        return False

def test_pages():
    """测试页面访问"""
    print("\n" + "=" * 60)
    print("3. 测试页面访问")
    print("=" * 60)
    
    pages = [
        ("登录页面", f"{BASE_URL}/login.html"),
        ("首页", f"{BASE_URL}/index.html"),
        ("计划页面", f"{BASE_URL}/plan.html"),
        ("设置页面", f"{BASE_URL}/settings.html"),
        ("回测页面", f"{BASE_URL}/backtest.html"),
        ("预测页面", f"{BASE_URL}/prediction.html"),
        ("策略页面", f"{BASE_URL}/strategy.html"),
    ]
    
    success_count = 0
    for name, url in pages:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: 访问成功")
                success_count += 1
            else:
                print(f"❌ {name}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print(f"\n页面访问成功率: {success_count}/{len(pages)}")
    return success_count == len(pages)

def test_api():
    """测试API接口"""
    print("\n" + "=" * 60)
    print("4. 测试API接口")
    print("=" * 60)
    
    apis = [
        ("股票池信息", f"{BASE_URL}/api/stockpool/info"),
        ("HS300成分股", f"{BASE_URL}/api/hs300/components"),
    ]
    
    success_count = 0
    for name, url in apis:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: 接口正常")
                success_count += 1
            else:
                print(f"❌ {name}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print(f"\nAPI接口成功率: {success_count}/{len(apis)}")
    return success_count >= len(apis) // 2

def test_login_validation():
    """测试登录验证"""
    print("\n" + "=" * 60)
    print("5. 测试登录验证")
    print("=" * 60)
    
    # 测试错误的密码
    data = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=data, timeout=5)
        result = response.json()
        
        if not result.get('success'):
            print("✅ 错误密码被正确拒绝")
            return True
        else:
            print("❌ 错误密码未被拒绝")
            return False
    except Exception as e:
        print(f"❌ 登录验证测试失败: {e}")
        return False

def test_page_security():
    """测试页面安全验证"""
    print("\n" + "=" * 60)
    print("6. 测试页面安全验证")
    print("=" * 60)
    
    protected_pages = [
        ("首页", f"{BASE_URL}/index.html"),
        ("计划页面", f"{BASE_URL}/plan.html"),
        ("设置页面", f"{BASE_URL}/settings.html"),
    ]
    
    success_count = 0
    for name, url in protected_pages:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                if 'checkLogin' in response.text:
                    print(f"✅ {name}: 包含登录验证")
                    success_count += 1
                else:
                    print(f"⚠️  {name}: 缺少登录验证")
            else:
                print(f"❌ {name}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print(f"\n安全验证覆盖率: {success_count}/{len(protected_pages)}")
    return success_count == len(protected_pages)

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("备份悟空52224 - 部署前测试")
    print("=" * 60)
    print(f"服务器地址: {BASE_URL}")
    print(f"测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    results.append(("服务器连接", test_connection()))
    results.append(("登录功能", test_login()))
    results.append(("页面访问", test_pages()))
    results.append(("API接口", test_api()))
    results.append(("登录验证", test_login_validation()))
    results.append(("安全验证", test_page_security()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    success_count = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:12s}: {status}")
        if result:
            success_count += 1
    
    print(f"\n总体成功率: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("\n🎉 所有测试通过！可以进行公网部署。")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查后再部署。")
        return 1

if __name__ == "__main__":
    sys.exit(main())