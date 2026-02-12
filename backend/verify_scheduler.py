import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app

print("=" * 50)
print("验证PDF调度器状态")
print("=" * 50)

# 检查PDF调度器状态
print("\nPDF调度器状态:")
print(f"  运行中: {app.pdf_scheduler.is_running()}")
print(f"  定时任务: {app.pdf_scheduler.get_scheduled_times()}")
print(f"  PDF导出回调: {app.pdf_scheduler.pdf_export_callback is not None}")
print(f"  邮件发送回调: {app.pdf_scheduler.email_send_callback is not None}")

print("\n" + "=" * 50)
print("验证完成")
print("=" * 50)