import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app

print("=" * 50)
print("测试定时PDF导出和邮件发送")
print("=" * 50)

# 1. 检查PDF调度器状态
print("\n1. PDF调度器状态:")
print(f"  运行中: {app.pdf_scheduler.is_running()}")
print(f"  定时任务: {app.pdf_scheduler.get_scheduled_times()}")
print(f"  PDF导出回调: {app.pdf_scheduler.pdf_export_callback is not None}")
print(f"  邮件发送回调: {app.pdf_scheduler.email_send_callback is not None}")

# 2. 手动执行PDF导出
print("\n2. 手动执行PDF导出:")
try:
    pdf_file_path = app.pdf_scheduler.pdf_export_callback()
    print(f"  PDF文件: {pdf_file_path}")
    
    if pdf_file_path and os.path.exists(pdf_file_path):
        print(f"  PDF文件存在")
        
        # 3. 手动执行邮件发送
        print("\n3. 手动执行邮件发送:")
        try:
            result = app.pdf_scheduler.email_send_callback(pdf_file_path)
            print(f"  邮件发送完成")
        except Exception as e:
            print(f"  邮件发送失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"  PDF文件不存在")
        
except Exception as e:
    print(f"  PDF导出失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)