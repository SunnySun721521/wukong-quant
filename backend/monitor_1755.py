import os
import time
import json
from datetime import datetime, timedelta

# 监控PDF自动导出定时任务执行情况
def monitor_pdf_scheduler():
    """监控PDF调度器执行情况"""
    
    # 文件路径
    config_path = os.path.join(os.path.dirname(__file__), 'data', 'pdf_scheduler_config.json')
    log_path = os.path.join(os.path.dirname(__file__), 'data', 'pdf_execution_log.json')
    scheduled_pdfs_dir = os.path.join(os.path.dirname(__file__), 'scheduled_pdfs')
    email_log_path = os.path.join(os.path.dirname(__file__), 'data', 'email_send_log.json')
    
    print(f"开始监控PDF自动导出定时任务执行情况...")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    scheduled_times = config.get('scheduled_times', [])
    
    # 查找17:55的配置
    target_time = None
    for time_config in scheduled_times:
        if time_config['hour'] == 17 and time_config['minute'] == 55:
            target_time = time_config
            break
    
    if not target_time:
        print("未找到17:55的定时任务配置")
        return
    
    print(f"监控目标时间: 17:55")
    print(f"监控开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取当前日期
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 监控循环
    while True:
        current_time = datetime.now()
        current_time_str = current_time.strftime('%H:%M:%S')
        current_date_str = current_time.strftime('%Y-%m-%d')
        
        print(f"\r当前时间: {current_time_str}", end="", flush=True)
        
        # 检查是否已经过了17:55
        if current_time.hour >= 18 or (current_time.hour == 17 and current_time.minute >= 55):
            print(f"\n\n已过17:55，检查执行情况...")
            
            # 检查执行日志
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                
                executions = log_data.get('executions', {})
                
                # 查找17:55的执行记录
                execution_key = None
                for key, value in executions.items():
                    if key.startswith(today) and "17:55" in value:
                        execution_key = key
                        break
                
                if execution_key:
                    print(f"✓ 17:55定时任务已执行，执行时间: {executions[execution_key]}")
                    
                    # 检查PDF文件
                    pdf_files = []
                    if os.path.exists(scheduled_pdfs_dir):
                        for file in os.listdir(scheduled_pdfs_dir):
                            if file.startswith('每日操作计划_') and file.endswith('.pdf'):
                                file_path = os.path.join(scheduled_pdfs_dir, file)
                                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                                if file_time.hour == 17 and file_time.minute >= 55:
                                    pdf_files.append((file, file_time))
                    
                    if pdf_files:
                        print(f"✓ 找到{len(pdf_files)}个17:55附近的PDF文件:")
                        for file, file_time in pdf_files:
                            print(f"  - {file} (创建时间: {file_time.strftime('%H:%M:%S')})")
                    else:
                        print("✗ 未找到17:55附近的PDF文件")
                    
                    # 检查邮件发送日志
                    if os.path.exists(email_log_path):
                        with open(email_log_path, 'r', encoding='utf-8') as f:
                            email_log_data = json.load(f)
                        
                        email_logs = email_log_data.get('logs', [])
                        
                        # 查找17:55附近的邮件发送记录
                        email_found = False
                        for log in email_logs:
                            if log.get('created_at', '').startswith(today):
                                log_time_str = log.get('created_at', '').split(' ')[1]
                                log_hour = int(log_time_str.split(':')[0])
                                log_minute = int(log_time_str.split(':')[1])
                                
                                if log_hour == 17 and log_minute >= 55:
                                    print(f"✓ 找到17:55附近的邮件发送记录:")
                                    print(f"  - 时间: {log.get('created_at', '')}")
                                    print(f"  - 状态: {log.get('status', '')}")
                                    print(f"  - PDF文件: {log.get('pdf_file', '')}")
                                    email_found = True
                                    break
                        
                        if not email_found:
                            print("✗ 未找到17:55附近的邮件发送记录")
                    else:
                        print("✗ 邮件发送日志文件不存在")
                else:
                    print("✗ 未找到17:55的执行记录")
            
            break
        
        # 每秒检查一次
        time.sleep(1)
    
    print("\n监控结束")

if __name__ == "__main__":
    try:
        monitor_pdf_scheduler()
    except KeyboardInterrupt:
        print("\n监控已中断")