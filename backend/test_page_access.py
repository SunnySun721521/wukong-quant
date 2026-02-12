#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

print("=== 测试页面访问控制 ===")

pages = [
    ('首页', 'http://127.0.0.1:5006/index.html'),
    ('计划', 'http://127.0.0.1:5006/plan.html'),
    ('设置', 'http://127.0.0.1:5006/settings.html'),
    ('回测', 'http://127.0.0.1:5006/backtest.html'),
    ('预测', 'http://127.0.0.1:5006/prediction.html'),
    ('策略', 'http://127.0.0.1:5006/strategy.html'),
]

for name, url in pages:
    try:
        response = requests.get(url)
        print(f"{name}: 状态码 {response.status_code}")
        
        if response.status_code == 200:
            if 'checkLogin' in response.text:
                print(f"  ✅ 包含登录验证代码")
            else:
                print(f"  ❌ 缺少登录验证代码")
        else:
            print(f"  ❌ 访问失败")
    except Exception as e:
        print(f"{name}: 请求异常 - {e}")

print("\n=== 测试完成 ===")