import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.email_config_db import EmailConfigDB

def init_email_recipients():
    """初始化接收邮箱数据"""
    db = EmailConfigDB()
    
    # 添加示例接收邮箱
    sample_recipients = [
        {
            'email_address': 'lib@tcscd.com',
            'name': '默认收件人',
            'description': '系统默认接收邮箱',
            'is_active': True
        }
    ]
    
    for recipient in sample_recipients:
        result = db.add_recipient(**recipient)
        if result:
            print(f"添加接收邮箱成功: {recipient['email_address']}")
        else:
            print(f"添加接收邮箱失败或已存在: {recipient['email_address']}")
    
    # 查询所有接收邮箱
    recipients = db.get_recipients()
    print(f"\n当前接收邮箱列表 ({len(recipients)} 个):")
    for recipient in recipients:
        print(f"- {recipient['email_address']} (姓名: {recipient['name']}, 状态: {'激活' if recipient['is_active'] else '禁用'})")

if __name__ == "__main__":
    init_email_recipients()