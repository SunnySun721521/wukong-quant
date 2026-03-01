#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF定时任务监控脚本
实时监控PDF自动导出定时任务的执行情况
"""

import os
import json
import time
from datetime import datetime

def get_project_path():
    """获取项目路径"""
    return os.path.dirname(os.path.abspath(__file__))

def read_config():
    """读取定时任务配置"""
    config_file = os.path.join(get_project_path(), 'backend', 'data', 'pdf_scheduler_config.json')
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"读取配置失败: {e}")
    return {"scheduled_times": []}

def read_execution_log():
    """读取执行日志"""
    log_file = os.path.join(get_project_path(), 'backend', 'data', 'pdf_execution_log.json')
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('executions', {})
    except Exception as e:
        print(f"读取执行日志失败: {e}")
    return {}

def read_app_log():
    """读取应用日志（最近的PDF相关日志）"""
    log_lines = []
    log_file = os.path.join(get_project_path(), 'backend', 'app.log')
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # 获取最后50行包含PDF或scheduler的日志
                for line in reversed(lines[-200:]):
                    if 'PDF' in line or 'scheduler' in line.lower() or '定时' in line or '邮件' in line:
                        log_lines.append(line.strip())
                    if len(log_lines) >= 20:
                        break
    except Exception as e:
        print(f"读取应用日志失败: {e}")
    return list(reversed(log_lines))

def format_time_list(times):
    """格式化时间列表"""
    return [f"{t['hour']:02d}:{t['minute']:02d}" for t in times]

def is_weekday():
    """判断今天是否是工作日"""
    return datetime.now().weekday() < 5

def main():
    print("=" * 80)
    print("📊 PDF定时任务监控系统")
    print("=" * 80)
    print(f"监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"今天是: {'工作日 ✅' if is_weekday() else '周末/节假日 ❌'}")
    print()
    
    # 读取配置
    config = read_config()
    scheduled_times = config.get('scheduled_times', [])
    
    print("⏰ 配置的定时任务时间:")
    if scheduled_times:
        for i, t in enumerate(scheduled_times, 1):
            time_str = f"{t['hour']:02d}:{t['minute']:02d}"
            print(f"   {i}. {time_str}")
    else:
        print("   暂无配置")
    print()
    
    # 读取执行日志
    executions = read_execution_log()
    today = datetime.now().strftime('%Y-%m-%d')
    
    print("📋 执行记录:")
    if executions:
        today_executions = {k: v for k, v in executions.items() if k.startswith(today)}
        if today_executions:
            print(f"   今天已执行 {len(today_executions)} 个任务:")
            for key, time_str in sorted(today_executions.items()):
                print(f"   - {key}: {time_str}")
        else:
            print("   今天尚未执行任何任务")
            print(f"   历史执行记录: {len(executions)} 条")
    else:
        print("   暂无执行记录")
    print()
    
    # 读取应用日志
    app_logs = read_app_log()
    if app_logs:
        print("📝 最近的PDF/定时任务相关日志:")
        for log in app_logs[-10:]:
            print(f"   {log}")
    else:
        print("📝 暂无相关日志")
    print()
    
    # 检查当前是否应该执行任务
    print("🔍 当前状态检查:")
    current_time = datetime.now()
    current_time_str = f"{current_time.hour:02d}:{current_time.minute:02d}"
    print(f"   当前时间: {current_time_str}")
    
    if scheduled_times and is_weekday():
        for t in scheduled_times:
            scheduled_time_str = f"{t['hour']:02d}:{t['minute']:02d}"
            execution_key = f"{today}_{scheduled_times.index(t)}"
            
            # 计算时间差（分钟）
            current_minutes = current_time.hour * 60 + current_time.minute
            scheduled_minutes = t['hour'] * 60 + t['minute']
            diff_minutes = abs(current_minutes - scheduled_minutes)
            
            if execution_key in executions:
                status = "✅ 已执行"
            elif diff_minutes <= 2:
                status = "🔄 即将执行/执行窗口期内"
            elif current_minutes < scheduled_minutes:
                status = "⏳ 待执行"
            else:
                status = "❌ 已错过"
            
            print(f"   {scheduled_time_str}: {status}")
    
    print()
    print("=" * 80)
    print("监控完成，等待下次检查...")
    print("=" * 80)

if __name__ == '__main__':
    main()
