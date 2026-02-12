import os
import sys
import time
import signal
import subprocess

def stop_existing_flask():
    """停止现有的Flask应用"""
    print("正在检查现有的Flask应用...")
    
    try:
        # 查找所有Python进程
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
        
        if python_processes:
            print(f"找到 {len(python_processes)} 个Flask应用实例，正在停止...")
            for proc in python_processes:
                try:
                    pid = proc['pid']
                    print(f"停止进程: PID={pid}")
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                 capture_output=True, text=True)
                except Exception as e:
                    print(f"停止进程失败: {e}")
            
            # 等待进程完全停止
            print("等待进程完全停止...")
            time.sleep(30)  # 确保至少30秒的间隔
            
            return True
        else:
            print("没有找到运行中的Flask应用实例")
            return False
            
    except Exception as e:
        print(f"检查进程失败: {e}")
        return False

def start_flask():
    """启动Flask应用"""
    print("启动Flask应用...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 使用单实例机制启动
    subprocess.Popen(['python', 'single_instance_flask.py'])

def restart_flask():
    """重启Flask应用"""
    print("=== Flask应用重启 ===")
    
    # 停止现有实例
    stopped = stop_existing_flask()
    
    # 启动新实例
    start_flask()
    
    print("=== Flask应用重启完成 ===")

if __name__ == "__main__":
    restart_flask()