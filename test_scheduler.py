#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF调度器是否正常工作
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from pdf_scheduler import PDFScheduler
from datetime import datetime

def test_scheduler():
    print("=" * 60)
    print("测试PDF调度器")
    print("=" * 60)
    
    # 创建调度器实例
    scheduler = PDFScheduler()
    
    print(f"\n1. 调度器配置:")
    print(f"   定时任务时间: {scheduler.get_scheduled_times()}")
    print(f"   只在工作日执行: {scheduler.get_only_weekday()}")
    print(f"   数据更新间隔: {scheduler.data_update_interval}分钟")
    
    print(f"\n2. 当前状态:")
    print(f"   当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   是否工作日: {scheduler.is_weekday()}")
    print(f"   是否交易时间: {scheduler.is_trading_time()}")
    print(f"   调度器是否运行: {scheduler.is_running()}")
    
    print(f"\n3. 执行记录:")
    executions = scheduler.last_execution_dates
    if executions:
        for key, time_str in executions.items():
            print(f"   - {key}: {time_str}")
    else:
        print("   暂无执行记录")
    
    print(f"\n4. 测试 should_execute_now:")
    should_execute = scheduler.should_execute_now()
    print(f"   是否应该执行: {should_execute}")
    
    print(f"\n5. 启动调度器:")
    scheduler.start()
    print(f"   调度器运行状态: {scheduler.is_running()}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    test_scheduler()
