#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务配置测试脚本
"""

import sys
import os
import json

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_scheduler_config():
    """测试定时任务配置"""
    print("=" * 60)
    print("定时任务配置测试")
    print("=" * 60)
    
    # 配置文件路径
    config_file = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'scheduler_config.json')
    execution_log_file = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'scheduler_execution_log.json')
    
    print(f"\n配置文件路径: {config_file}")
    print(f"执行日志路径: {execution_log_file}")
    
    # 读取定时任务配置
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("\n定时任务配置:")
        print(f"  定时时间: {config.get('scheduled_times', [])}")
        print(f"  仅工作日执行: {config.get('only_weekday', True)}")
    else:
        print("\n❌ 配置文件不存在")
        print("  使用默认配置: [{'hour': 12, 'minute': 0}, {'hour': 15, 'minute': 30}]")
    
    # 读取执行日志
    if os.path.exists(execution_log_file):
        with open(execution_log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        executions = log_data.get('executions', {})
        print("\n执行记录:")
        if executions:
            for key, time_str in sorted(executions.items()):
                print(f"  {key}: {time_str}")
        else:
            print("  暂无执行记录")
    else:
        print("\n❌ 执行日志文件不存在")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_scheduler_config()
