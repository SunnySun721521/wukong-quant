#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务监测脚本
用于监测PDF定时任务的执行情况
"""

import json
import os
from datetime import datetime, timedelta
import time

# 时区配置 - 使用北京时间 (UTC+8)
TIMEZONE_OFFSET = timedelta(hours=8)

def get_beijing_time():
    """获取北京时间"""
    return datetime.utcnow() + TIMEZONE_OFFSET

def get_beijing_time_str():
    """获取北京时间字符串"""
    return get_beijing_time().strftime('%H:%M:%S')

def get_beijing_date_str():
    """获取北京日期字符串"""
    return get_beijing_time().strftime('%Y-%m-%d')

def load_execution_log():
    """加载执行日志"""
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'data', 'scheduler_execution_log.json')
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"读取执行日志失败: {e}")
    return {'executions': {}}

def load_scheduler_config():
    """加载定时任务配置"""
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'data', 'scheduler_config.json')
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"读取定时任务配置失败: {e}")
    return {'scheduled_times': [], 'only_weekday': True}

def monitor():
    """监测定时任务"""
    print("=" * 60)
    print("PDF定时任务监测器")
    print("=" * 60)
    print(f"当前北京时间: {get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 加载配置
    config = load_scheduler_config()
    scheduled_times = config.get('scheduled_times', [])
    
    print("配置的定时任务时间:")
    for i, scheduled in enumerate(scheduled_times):
        print(f"  [{i}] {scheduled['hour']:02d}:{scheduled['minute']:02d}")
    print()
    
    # 加载执行日志
    log_data = load_execution_log()
    executions = log_data.get('executions', {})
    
    print("已执行的任务记录:")
    if executions:
        for key, time_str in sorted(executions.items()):
            print(f"  {key}: {time_str}")
    else:
        print("  暂无执行记录")
    print()
    
    # 检查即将到来的任务
    now = get_beijing_time()
    current_time_minutes = now.hour * 60 + now.minute
    
    print("任务状态检查:")
    current_date_str = get_beijing_date_str()
    
    for i, scheduled in enumerate(scheduled_times):
        scheduled_minutes = scheduled['hour'] * 60 + scheduled['minute']
        time_diff = scheduled_minutes - current_time_minutes
        execution_key = f"{current_date_str}_{i}"
        
        if execution_key in executions:
            status = "✅ 已执行"
        elif time_diff < 0:
            status = "❌ 已过期"
        elif time_diff <= 10:
            status = f"⏳ 即将执行（{time_diff}分钟后）"
        else:
            status = f"⏸️ 等待中（{time_diff}分钟后）"
        
        print(f"  [{i}] {scheduled['hour']:02d}:{scheduled['minute']:02d} - {status}")
    
    print()
    print("=" * 60)
    print("监测完成")
    print("=" * 60)

if __name__ == '__main__':
    monitor()
