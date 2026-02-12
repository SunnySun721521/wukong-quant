import os
import sys
import time
import fcntl
import signal

class SingleInstance:
    """确保只有一个应用实例在运行"""
    
    def __init__(self, lock_file):
        self.lock_file = lock_file
        
        try:
            # 尝试创建锁文件
            self.fp = open(self.lock_file, 'w')
            # 尝试获取文件锁
            fcntl.flock(self.fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.is_running = False
        except (IOError, OSError):
            # 锁文件已被其他进程占用
            self.fp = None
            self.is_running = True
    
    def __enter__(self):
        return self.is_running is False
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fp:
            try:
                # 释放文件锁
                fcntl.flock(self.fp.fileno(), fcntl.LOCK_UN)
                self.fp.close()
                # 删除锁文件
                os.unlink(self.lock_file)
            except:
                pass

# Windows版本的实现
class SingleInstanceWindows:
    """确保只有一个应用实例在运行 (Windows版本)"""
    
    def __init__(self, lock_file):
        self.lock_file = lock_file
        
        try:
            # 尝试创建锁文件
            if os.path.exists(self.lock_file):
                # 检查锁文件中的进程是否仍在运行
                with open(self.lock_file, 'r') as f:
                    pid = int(f.read().strip())
                
                try:
                    # 尝试向进程发送信号(0)，检查是否存在
                    os.kill(pid, 0)
                    self.is_running = True
                    self.fp = None
                    return
                except OSError:
                    # 进程不存在，可以创建新实例
                    pass
            
            # 创建新的锁文件
            self.fp = open(self.lock_file, 'w')
            self.fp.write(str(os.getpid()))
            self.fp.flush()
            self.is_running = False
            
        except Exception as e:
            print(f"创建单实例锁失败: {e}")
            self.is_running = True
            self.fp = None
    
    def __enter__(self):
        return self.is_running is False
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fp:
            try:
                self.fp.close()
                os.unlink(self.lock_file)
            except:
                pass

# 根据操作系统选择合适的实现
if os.name == 'nt':  # Windows
    SingleInstanceImpl = SingleInstanceWindows
else:  # Unix/Linux
    SingleInstanceImpl = SingleInstance

def ensure_single_flask_instance():
    """确保只有一个Flask应用实例在运行"""
    lock_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.flask_app.lock')
    
    with SingleInstanceImpl(lock_file) as can_start:
        if can_start:
            print("启动Flask应用实例...")
            # 导入并启动Flask应用
            import app
            app.run_app()
        else:
            print("Flask应用实例已在运行，无需启动新实例")
            return False
    
    return True

if __name__ == "__main__":
    ensure_single_flask_instance()