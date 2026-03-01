import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import _send_email_notification

def test_email_callback():
    """测试邮件发送回调函数"""
    print("开始测试邮件发送回调函数...")
    
    # 17:55的PDF文件路径
    pdf_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'backend', 
        'scheduled_pdfs', 
        '每日操作计划_20260209_175439.pdf'
    )
    
    if not os.path.exists(pdf_file_path):
        print(f"PDF文件不存在: {pdf_file_path}")
        return False
    
    print(f"测试PDF文件: {pdf_file_path}")
    
    try:
        # 调用邮件发送回调函数
        _send_email_notification(pdf_file_path)
        print("邮件发送回调函数执行完成")
        return True
    except Exception as e:
        print(f"测试邮件发送回调函数异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_email_callback()