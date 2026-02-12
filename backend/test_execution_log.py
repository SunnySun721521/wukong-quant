#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

# 测试执行记录API
print("=== 测试PDF自动导出定时任务执行记录 ===")

try:
    response = requests.get('http://127.0.0.1:5006/api/scheduler/execution-log')
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        executions = data.get('executions', [])
        
        print(f"\n总执行记录数: {len(executions)}")
        print(f"显示的执行记录数: {len(executions)}")
        
        if len(executions) > 5:
            print(f"⚠️  警告: 执行记录数超过5条，当前显示{len(executions)}条")
        else:
            print(f"✅ 执行记录数符合要求（最多5条）")
        
        print("\n执行记录详情:")
        for i, execution in enumerate(executions, 1):
            print(f"{i}. 日期: {execution.get('date', 'N/A')}, 时间: {execution.get('time', 'N/A')}, Key: {execution.get('key', 'N/A')}")
    else:
        print(f"请求失败: {response.text}")
        
except Exception as e:
    print(f"请求异常: {e}")

print("\n=== 测试完成 ===")