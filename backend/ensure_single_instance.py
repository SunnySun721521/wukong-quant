import os
import sys
import time
import psutil
import signal

def check_and_ensure_single_instance():
    """检查并确保只有一个Flask应用实例在运行"""
    
    # 获取当前脚本路径
    current_script = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_script)
    app_path = os.path.join(current_dir, 'app.py')
    
    print(f"当前应用路径: {app_path}")
    
    # 查找所有运行中的Python进程
    python_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # 检查是否是Python进程
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline and len(cmdline) > 1:
                    # 检查是否是运行我们的Flask应用
                    if any('app.py' in arg for arg in cmdline):
                        python_processes.append(proc.info)
                        print(f"找到Flask应用进程: PID={proc.info['pid']}, 命令行={' '.join(cmdline)}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if not python_processes:
        print("没有找到运行中的Flask应用实例")
        return True
    
    # 如果有多个Flask应用实例，保留最新的一个
    if len(python_processes) > 1:
        print(f"发现 {len(python_processes)} 个Flask应用实例，将保留最新的一个")
        
        # 按启动时间排序，保留最新的
        python_processes.sort(key=lambda x: x['pid'], reverse=True)
        
        # 保留最新的进程，终止其他进程
        for i, proc in enumerate(python_processes):
            if i < len(python_processes) - 1:  # 不是最新的进程
                try:
                    pid = proc['pid']
                    print(f"终止旧进程: PID={pid}")
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)  # 等待进程终止
                    
                    # 如果进程仍在运行，强制终止
                    if psutil.pid_exists(pid):
                        os.kill(pid, signal.SIGKILL)
                        print(f"强制终止进程: PID={pid}")
                except Exception as e:
                    print(f"终止进程失败: {e}")
    
    # 返回是否需要启动新实例
    latest_process = python_processes[-1] if python_processes else None
    if latest_process:
        print(f"保留的Flask应用实例: PID={latest_process['pid']}")
        return False  # 已有实例在运行，不需要启动新实例
    
    return True  # 没有实例在运行，需要启动新实例

if __name__ == "__main__":
    need_start = check_and_ensure_single_instance()
    if need_start:
        print("需要启动新的Flask应用实例")
    else:
        print("Flask应用实例已在运行")