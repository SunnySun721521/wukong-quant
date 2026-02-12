import os
import sys
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.email_sender import EmailSender
from backend.email_config_manager import EmailConfigManager
from backend.email_template_engine import EmailTemplateEngine
from backend.email_logger import EmailLogger

def test_email_sending():
    """测试邮件发送功能"""
    print("开始测试邮件发送功能...")
    
    # 创建邮件发送器
    email_sender = EmailSender(
        config_manager=EmailConfigManager(),
        template_engine=EmailTemplateEngine(),
        logger=EmailLogger()
    )
    
    # 获取邮件配置
    email_config = email_sender.config_manager.get_config()
    print(f"邮件配置: {json.dumps(email_config, indent=2, ensure_ascii=False)}")
    
    # 检查是否启用邮件发送
    if not email_config.get('enabled', False):
        print("邮件发送未启用")
        return False
    
    # 创建测试PDF文件
    test_pdf_path = os.path.join(os.path.dirname(__file__), 'test_email.pdf')
    with open(test_pdf_path, 'w') as f:
        f.write("这是一个测试PDF文件")
    
    # 测试市场数据
    market_data = {
        'market_status': '牛市',
        'current_position': '60%',
        'total_assets': '¥250,000.00'
    }
    
    try:
        # 建立SMTP连接
        print("建立SMTP连接...")
        if not email_sender.connect_smtp(email_config):
            print("SMTP连接失败")
            return False
        
        # 发送邮件
        print("发送邮件...")
        success, error_msg = email_sender.send_email(test_pdf_path, market_data)
        
        # 断开SMTP连接
        email_sender.disconnect_smtp()
        
        if success:
            print("邮件发送成功")
            return True
        else:
            print(f"邮件发送失败: {error_msg}")
            return False
            
    except Exception as e:
        print(f"测试邮件发送异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理测试文件
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)

if __name__ == "__main__":
    test_email_sending()