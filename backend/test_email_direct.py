import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接调用邮件发送回调函数
pdf_file_path = r"D:\trae\备份悟空52220\backend\scheduled_pdfs\每日操作计划_20260209_175439.pdf"

print(f"测试PDF文件: {pdf_file_path}")
print(f"文件存在: {os.path.exists(pdf_file_path)}")

if os.path.exists(pdf_file_path):
    try:
        # 导入邮件发送相关模块
        from backend.email_sender import EmailSender
        from backend.email_config_manager import EmailConfigManager
        from backend.email_template_engine import EmailTemplateEngine
        from backend.email_logger import EmailLogger
        
        # 创建邮件发送器
        email_sender = EmailSender(
            config_manager=EmailConfigManager(),
            template_engine=EmailTemplateEngine(),
            logger=EmailLogger()
        )
        
        # 获取邮件配置
        email_config = email_sender.config_manager.get_config()
        print(f"邮件启用: {email_config.get('enabled', False)}")
        
        if email_config.get('enabled', False):
            # 建立SMTP连接
            print("建立SMTP连接...")
            if email_sender.connect_smtp(email_config):
                print("SMTP连接成功")
                
                # 测试市场数据
                market_data = {
                    'market_status': '牛市',
                    'current_position': '60%',
                    'total_assets': '¥250,000.00'
                }
                
                # 发送邮件
                print("发送邮件...")
                success, error_msg = email_sender.send_email(pdf_file_path, market_data)
                
                # 断开SMTP连接
                email_sender.disconnect_smtp()
                
                if success:
                    print("邮件发送成功")
                else:
                    print(f"邮件发送失败: {error_msg}")
            else:
                print("SMTP连接失败")
        else:
            print("邮件发送未启用")
            
    except Exception as e:
        print(f"测试邮件发送异常: {e}")
        import traceback
        traceback.print_exc()
else:
    print("PDF文件不存在")