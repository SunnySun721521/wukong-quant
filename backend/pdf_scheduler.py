import threading
import time
from datetime import datetime, time as dt_time, timedelta
import json
import os
from typing import List, Dict, Callable, Optional

# 时区配置 - 使用北京时间 (UTC+8)
TIMEZONE_OFFSET = timedelta(hours=8)

def get_beijing_time():
    """获取北京时间"""
    return datetime.utcnow() + TIMEZONE_OFFSET

def get_beijing_date_str():
    """获取北京日期字符串"""
    return (datetime.utcnow() + TIMEZONE_OFFSET).strftime('%Y-%m-%d')

def get_beijing_time_str():
    """获取北京时间字符串"""
    return (datetime.utcnow() + TIMEZONE_OFFSET).strftime('%H:%M:%S')

def get_beijing_datetime_str():
    """获取北京日期时间字符串"""
    return (datetime.utcnow() + TIMEZONE_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

class PDFScheduler:
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), 'data', 'pdf_scheduler_config.json')
        self.execution_log_file = os.path.join(os.path.dirname(__file__), 'data', 'pdf_execution_log.json')
        self.data_update_log_file = os.path.join(os.path.dirname(__file__), 'data', 'data_update_log.json')
        self.scheduled_times = []
        self.running = False
        self.scheduler_thread = None
        self.pdf_export_callback = None
        self.email_send_callback = None
        self.data_update_callbacks = []
        self.last_execution_dates = {}
        self.data_update_interval = 10
        self.last_data_update_time = None
        self.task_executing = False  # 添加任务执行状态跟踪
        self.only_weekday = True  # 默认只在工作日执行
        self.load_config()
        self.load_execution_log()
        self.load_data_update_config()
    
    def load_config(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.scheduled_times = config.get('scheduled_times', [])
                    self.only_weekday = config.get('only_weekday', True)
                    print(f"加载定时任务配置: {self.scheduled_times}, 仅工作日执行: {self.only_weekday}")
            else:
                self.scheduled_times = [
                    {'hour': 12, 'minute': 0},
                    {'hour': 15, 'minute': 30}
                ]
                self.only_weekday = True
                self.save_config()
                print(f"使用默认定时任务配置: {self.scheduled_times}, 仅工作日执行: {self.only_weekday}")
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.scheduled_times = [
                {'hour': 12, 'minute': 0},
                {'hour': 15, 'minute': 30}
            ]
            self.only_weekday = True
    
    def save_config(self):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'scheduled_times': self.scheduled_times,
                    'only_weekday': self.only_weekday
                }, f, ensure_ascii=False, indent=2)
            print(f"保存定时任务配置: {self.scheduled_times}, 仅工作日执行: {self.only_weekday}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def load_execution_log(self):
        """加载执行日志"""
        try:
            if os.path.exists(self.execution_log_file):
                with open(self.execution_log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    self.last_execution_dates = log_data.get('executions', {})
                    print(f"加载执行日志: {self.last_execution_dates}")
            else:
                self.last_execution_dates = {}
        except Exception as e:
            print(f"加载执行日志失败: {e}")
            self.last_execution_dates = {}
    
    def save_execution_log(self):
        """保存执行日志"""
        try:
            os.makedirs(os.path.dirname(self.execution_log_file), exist_ok=True)
            with open(self.execution_log_file, 'w', encoding='utf-8') as f:
                json.dump({'executions': self.last_execution_dates}, f, ensure_ascii=False, indent=2)
            print(f"保存执行日志: {self.last_execution_dates}")
        except Exception as e:
            print(f"保存执行日志失败: {e}")
    
    def set_scheduled_times(self, times: List[Dict[str, int]]):
        """设置定时执行时间"""
        self.scheduled_times = times
        self.save_config()
        print(f"更新定时任务配置: {self.scheduled_times}")
    
    def get_scheduled_times(self) -> List[Dict[str, int]]:
        """获取定时执行时间"""
        return self.scheduled_times
    
    def set_only_weekday(self, only_weekday: bool):
        """设置是否只在工作日执行"""
        self.only_weekday = only_weekday
        self.save_config()
        print(f"更新仅工作日执行设置: {self.only_weekday}")
    
    def get_only_weekday(self) -> bool:
        """获取是否只在工作日执行"""
        return self.only_weekday
    
    def set_pdf_export_callback(self, callback: Callable):
        """设置PDF导出回调函数"""
        self.pdf_export_callback = callback
    
    def add_data_update_callback(self, callback: Callable):
        """添加数据更新回调函数"""
        self.data_update_callbacks.append(callback)
    
    def set_email_send_callback(self, callback: Callable):
        """设置邮件发送回调函数"""
        self.email_send_callback = callback
    
    def load_data_update_config(self):
        """加载数据更新配置"""
        try:
            config_file = os.path.join(os.path.dirname(self.data_update_log_file), 'data_update_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.data_update_interval = config.get('update_interval', 10)
                    print(f"加载数据更新配置: 间隔={self.data_update_interval}分钟")
            else:
                self.data_update_interval = 10
                print("使用默认数据更新间隔: 10分钟")
        except Exception as e:
            print(f"加载数据更新配置失败: {e}")
            self.data_update_interval = 10
    
    def save_data_update_config(self):
        """保存数据更新配置"""
        try:
            config_file = os.path.join(os.path.dirname(self.data_update_log_file), 'data_update_config.json')
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({'update_interval': self.data_update_interval}, f, ensure_ascii=False, indent=2)
            print(f"保存数据更新配置: 间隔={self.data_update_interval}分钟")
        except Exception as e:
            print(f"保存数据更新配置失败: {e}")
    
    def set_data_update_interval(self, interval: int):
        """设置数据更新间隔"""
        self.data_update_interval = interval
        self.save_data_update_config()
    
    def log_data_update(self, module: str, success: bool, error: str = None):
        """记录数据更新日志"""
        try:
            log_entry = {
                'timestamp': get_beijing_datetime_str(),
                'module': module,
                'success': success,
                'error': error
            }
            
            if os.path.exists(self.data_update_log_file):
                with open(self.data_update_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            os.makedirs(os.path.dirname(self.data_update_log_file), exist_ok=True)
            with open(self.data_update_log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            status = "成功" if success else "失败"
            error_msg = f", 错误: {error}" if error else ""
            print(f"数据更新日志: [{get_beijing_datetime_str()}] {module} {status}{error_msg}")
        except Exception as e:
            print(f"记录数据更新日志失败: {e}")
    
    def is_weekday(self, dt: datetime = None) -> bool:
        """判断是否为工作日（周一至周五）"""
        if dt is None:
            dt = get_beijing_time()
        return dt.weekday() < 5
    
    def is_trading_time(self, dt: datetime = None) -> bool:
        """判断当前时间是否在股票交易时间段内"""
        if dt is None:
            dt = get_beijing_time()
        
        if not self.is_weekday(dt):
            return False
        
        current_time = dt_time(dt.hour, dt.minute, dt.second)
        
        # 上午交易时间：9:30 - 11:30
        morning_start = dt_time(9, 30, 0)
        morning_end = dt_time(11, 30, 0)
        
        # 下午交易时间：13:00 - 15:00
        afternoon_start = dt_time(13, 0, 0)
        afternoon_end = dt_time(15, 0, 0)
        
        return (morning_start <= current_time <= morning_end) or (afternoon_start <= current_time <= afternoon_end)
    
    def should_execute_now(self) -> bool:
        """判断当前时间是否应该执行任务（使用北京时间）"""
        now = get_beijing_time()
        
        current_date_str = get_beijing_date_str()
        current_time = dt_time(now.hour, now.minute, now.second)
        
        # 找到最接近的调度时间
        closest_index = -1
        closest_diff = float('inf')
        
        for i, scheduled in enumerate(self.scheduled_times):
            scheduled_time = dt_time(scheduled['hour'], scheduled['minute'], 0)
            # 检查是否是当前时间点（允许5分钟的误差，适应云平台休眠情况）
            time_diff = abs((current_time.hour * 3600 + current_time.minute * 60 + current_time.second) - 
                          (scheduled_time.hour * 3600 + scheduled_time.minute * 60))
            
            if time_diff <= 300 and time_diff < closest_diff:  # 放宽到5分钟
                closest_diff = time_diff
                closest_index = i
        
        # 如果找到最接近的调度时间且未执行过
        if closest_index >= 0:
            execution_key = f"{current_date_str}_{closest_index}"
            if execution_key not in self.last_execution_dates:
                # 立即标记为已执行，防止重复执行
                self.last_execution_dates[execution_key] = get_beijing_time_str()
                self.save_execution_log()
                print(f"触发定时任务: {current_date_str} {closest_index} {get_beijing_time_str()} (北京时间)")
                return True
            else:
                # 已执行过，检查是否超过1小时（防止跨天时重复执行）
                last_exec_time_str = self.last_execution_dates[execution_key]
                try:
                    last_exec_time = datetime.strptime(f"{current_date_str} {last_exec_time_str}", "%Y-%m-%d %H:%M:%S")
                    if (now - last_exec_time).total_seconds() > 3600:  # 超过1小时
                        print(f"任务已执行但超过1小时，允许重新执行: {execution_key}")
                        self.last_execution_dates[execution_key] = get_beijing_time_str()
                        self.save_execution_log()
                        return True
                except:
                    pass
        
        return False
    
    def execute_pdf_export(self):
        """执行PDF导出"""
        # 检查是否有任务正在执行
        if self.task_executing:
            print("前一个PDF导出任务仍在执行中，跳过本次执行")
            return
            
        self.task_executing = True
        
        if self.pdf_export_callback:
            try:
                print(f"执行定时PDF导出任务: {get_beijing_datetime_str()}")
                pdf_file_path = self.pdf_export_callback()
                print(f"定时PDF导出任务完成: {get_beijing_datetime_str()}")
                
                # 触发邮件发送
                if self.email_send_callback and pdf_file_path:
                    try:
                        print(f"触发邮件发送: {get_beijing_datetime_str()}")
                        self.email_send_callback(pdf_file_path)
                        print(f"邮件发送任务完成: {get_beijing_datetime_str()}")
                    except Exception as e:
                        print(f"邮件发送失败: {e}")
                        import traceback
                        traceback.print_exc()
                
                # 记录实际执行时间（使用北京时间）
                current_date_str = get_beijing_date_str()
                execution_key = f"{current_date_str}_{len(self.last_execution_dates)}"
                self.last_execution_dates[execution_key] = get_beijing_time_str()
                self.save_execution_log()
                print(f"PDF导出任务已记录: {execution_key} {get_beijing_time_str()} (北京时间)")
                
            except Exception as e:
                print(f"定时PDF导出任务失败: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # 无论成功还是失败，都重置任务执行状态
                self.task_executing = False
                print(f"任务执行状态已重置: {get_beijing_datetime_str()}")
        else:
            print("PDF导出回调函数未设置")
            self.task_executing = False
    
    def _scheduler_loop(self):
        """调度器主循环"""
        last_data_update_time = None
        last_task_execution_time = None
        
        print(f"调度器启动，当前时间: {get_beijing_datetime_str()} (北京时间)")
        print(f"定时任务配置: {self.scheduled_times}")
        print(f"数据更新间隔: {self.data_update_interval}分钟")
        
        while self.running:
            try:
                now = get_beijing_time()
                current_time_str = get_beijing_time_str()
                
                # 检查是否需要执行PDF导出
                if self.should_execute_now():
                    # 检查距离上次任务执行是否足够间隔（至少5分钟）
                    if last_task_execution_time is None or (now - last_task_execution_time).total_seconds() >= 300:
                        print(f"触发定时PDF导出任务: {current_time_str} (北京时间)")
                        self.execute_pdf_export()
                        last_task_execution_time = now
                    else:
                        print(f"PDF任务间隔不足5分钟，跳过执行: {current_time_str} (北京时间)")
                
                # 检查是否需要更新数据（只在交易时间段内执行）
                if self.is_trading_time(now):
                    if last_data_update_time is None or (now - last_data_update_time).total_seconds() >= self.data_update_interval * 60:
                        print(f"触发数据更新: {get_beijing_time_str()} (北京时间)")
                        self._execute_data_updates()
                        last_data_update_time = now
                        print(f"数据更新完成: {get_beijing_time_str()} (北京时间)")
                else:
                    # 非交易时间，重置last_data_update_time以便下次进入交易时间时立即更新
                    last_data_update_time = None
                    print(f"非交易时间，重置数据更新时间: {get_beijing_time_str()} (北京时间)")
                
                time.sleep(10)
            except Exception as e:
                print(f"调度器循环异常: {e}")
                time.sleep(10)
    
    def _execute_data_updates(self):
        """执行所有数据更新回调"""
        for callback in self.data_update_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"数据更新回调执行失败: {e}")
                import traceback
                traceback.print_exc()
    
    def start(self):
        """启动调度器"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            print("PDF定时任务调度器已启动")
            time_strs = [f"{t['hour']:02d}:{t['minute']:02d}" for t in self.scheduled_times]
            print(f"定时执行时间: {time_strs}")
        else:
            print("调度器已在运行中")
    
    def stop(self):
        """停止调度器"""
        if self.running:
            self.running = False
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5)
            print("PDF定时任务调度器已停止")
        else:
            print("调度器未运行")
    
    def is_running(self) -> bool:
        """检查调度器是否在运行"""
        return self.running
    
    def get_execution_log(self) -> List[Dict]:
        """获取执行日志"""
        return [
            {
                'key': key,
                'time': time_str,
                'date': key.split('_')[0] if '_' in key else key
            }
            for key, time_str in sorted(self.last_execution_dates.items(), key=lambda x: x[0], reverse=True)
        ][:5]
