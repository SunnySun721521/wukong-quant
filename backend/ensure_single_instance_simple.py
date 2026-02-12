import os
import sys
import time
import signal
import subprocess

def check_and_ensure_single_instance():
    """检查并确保只有一个Flask应用实例在运行"""
    
    # 获取当前脚本路径
    current_script = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_script)
    app_path = os.path.join(current_dir, 'app.py')
    
    print(f"当前应用路径: {app_path}")
    
    # 使用Windows命令查找Python进程
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], 
                          capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        python_processes = []
        for line in lines[1:]:  # 跳过标题行
            if line.strip():
                parts = line.split(',')
                if len(parts) >= 2:
                    pid = parts[1].strip()
                    # 检查命令行参数
                    try:
                        cmd_result = subprocess.run(['wmic', 'process', 'where', f'processid={pid}', 'get', 'commandline'], 
                                              capture_output=True, text=True)
                        cmdline = cmd_result.stdout
                        if 'app.py' in cmdline:
                            python_processes.append({
                                'pid': int(pid),
                                'cmdline': cmdline
                            })
                            print(f"找到Flask应用进程: PID={pid}")
                    except:
                        pass
        
        if not python_processes:
            print("没有找到运行中的Flask应用实例")
            return True
        
        # 如果有多个Flask应用实例，保留最新的一个
        if len(python_processes) > 1:
            print(f"发现 {len(python_processes)} 个Flask应用实例，将保留最新的一个")
            
            # 按PID排序，保留最新的（通常PID越大越新）
            python_processes.sort(key=lambda x: x['pid'])
            
            # 保留最新的进程，终止其他进程
            for i, proc in enumerate(python_processes[:-1]):  # 除了最新的进程
                try:
                    pid = proc['pid']
                    print(f"终止旧进程: PID={pid}")
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                 capture_output=True, text=True)
                except Exception as e:
                    print(f"终止进程失败: {e}")
        
        # 返回是否需要启动新实例
        latest_process = python_processes[-1] if python_processes else None
        if latest_process:
            print(f"保留的Flask应用实例: PID={latest_process['pid']}")
            return False  # 已有实例在运行，不需要启动新实例
        
        return True  # 没有实例在运行，需要启动新实例
        
    except Exception as e:
        print(f"检查进程失败: {e}")
        return True  # 出错时允许启动新实例

if __name__ == "__main__":
    need_start = check_and_ensure_single_instance()
    if need_start:
        print("需要启动新的Flask应用实例")
    else:
        print("Flask应用实例已在运行，无需启动新实例")