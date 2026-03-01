#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF调度器 - 模拟15:10任务执行
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from pdf_scheduler import PDFScheduler
from datetime import datetime, time as dt_time

def test_scheduler_at_1510():
    print("=" * 60)
    print("测试PDF调度器 - 验证任务检测逻辑")
    print("=" * 60)
    
    # 创建调度器实例
    scheduler = PDFScheduler()
    
    print(f"\n1. 当前实际时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"2. 配置的定时任务: {scheduler.get_scheduled_times()}")
    print(f"3. 当前执行记录: {scheduler.last_execution_dates}")
    
    # 手动测试 should_execute_now
    print(f"\n4. 测试 should_execute_now():")
    result = scheduler.should_execute_now()
    print(f"   结果: {result}")
    
    # 显示当前时间和最近任务的时间差
    now = datetime.now()
    current_time = dt_time(now.hour, now.minute, now.second)
    print(f"\n5. 时间分析:")
    print(f"   当前时间: {current_time}")
    
    for i, scheduled in enumerate(scheduler.scheduled_times):
        scheduled_time = dt_time(scheduled['hour'], scheduled['minute'], 0)
        time_diff = abs((current_time.hour * 3600 + current_time.minute * 60 + current_time.second) - 
                      (scheduled_time.hour * 3600 + scheduled_time.minute * 60))
        
        execution_key = f"{now.strftime('%Y-%m-%d')}_{i}"
        is_executed = execution_key in scheduler.last_execution_dates
        
        status = "✅ 已执行" if is_executed else "⏳ 未执行"
        within_window = "🔄 在窗口内" if time_diff <= 120 else "❌ 不在窗口内"
        
        print(f"   任务 {i}: {scheduled['hour']:02d}:{scheduled['minute']:02d} - {status} - {within_window} (差{time_diff}秒)")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_scheduler_at_1510()
