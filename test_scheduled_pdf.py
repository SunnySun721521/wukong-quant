#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_scheduled_pdf_export():
    """测试定时PDF导出和邮件发送功能"""
    try:
        # 1. 检查定时任务配置
        print("检查定时任务配置...")
        response = requests.get('http://127.0.0.1:5006/api/scheduler/config')
        config = response.json()
        print(f"定时任务配置: {config}")
        
        # 2. 检查邮件配置
        print("\n检查邮件配置...")
        response = requests.get('http://127.0.0.1:5006/api/email/config')
        email_config = response.json()
        print(f"邮件配置: {email_config}")
        
        # 3. 手动触发一次PDF导出和邮件发送
        print("\n手动触发PDF导出...")
        response = requests.get('http://127.0.0.1:5006/api/plan/export-pdf')
        if response.status_code == 200:
            result = response.json()
            print(f"PDF导出结果: {result}")
            
            # 4. 检查邮件发送日志
            print("\n检查邮件发送日志...")
            response = requests.get('http://127.0.0.1:5006/api/email/logs')
            logs = response.json()
            print(f"最近邮件发送日志: {logs[:2] if logs else '无日志'}")
        else:
            print(f"PDF导出失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_scheduled_pdf_export()