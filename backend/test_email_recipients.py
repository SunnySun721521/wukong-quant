import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.email_config_db import EmailConfigDB
from backend.email_config_manager import EmailConfigManager

def test_email_recipients_management():
    """测试接收邮箱管理功能"""
    print("=" * 50)
    print("测试接收邮箱管理功能")
    print("=" * 50)
    
    db = EmailConfigDB()
    config_manager = EmailConfigManager()
    
    # 1. 测试添加接收邮箱
    print("\n1. 测试添加接收邮箱")
    test_recipients = [
        {
            'email_address': 'test1@example.com',
            'name': '测试用户1',
            'description': '测试邮箱1',
            'is_active': True
        },
        {
            'email_address': 'test2@example.com',
            'name': '测试用户2',
            'description': '测试邮箱2',
            'is_active': True
        }
    ]
    
    for recipient in test_recipients:
        result = db.add_recipient(**recipient)
        print(f"添加 {recipient['email_address']}: {'成功' if result else '失败'}")
    
    # 2. 测试获取接收邮箱列表
    print("\n2. 测试获取接收邮箱列表")
    recipients = db.get_recipients(active_only=True)
    print(f"激活的接收邮箱数量: {len(recipients)}")
    for recipient in recipients:
        print(f"  - {recipient['email_address']} ({recipient['name']})")
    
    # 3. 测试更新接收邮箱
    print("\n3. 测试更新接收邮箱")
    if recipients:
        recipient_id = recipients[0]['id']
        result = db.update_recipient(recipient_id, name='更新后的姓名')
        print(f"更新接收邮箱ID {recipient_id}: {'成功' if result else '失败'}")
    
    # 4. 测试切换激活状态
    print("\n4. 测试切换激活状态")
    if recipients:
        recipient_id = recipients[0]['id']
        result = db.update_recipient(recipient_id, is_active=False)
        print(f"禁用接收邮箱ID {recipient_id}: {'成功' if result else '失败'}")
        
        # 验证只获取激活的邮箱
        active_recipients = db.get_recipients(active_only=True)
        print(f"激活的接收邮箱数量: {len(active_recipients)}")
    
    # 5. 测试配置管理器获取收件人列表
    print("\n5. 测试配置管理器获取收件人列表")
    config = config_manager.get_config()
    print(f"配置中的收件人数量: {len(config.get('recipients', []))}")
    for recipient_email in config.get('recipients', []):
        print(f"  - {recipient_email}")
    
    # 6. 清理测试数据
    print("\n6. 清理测试数据")
    all_recipients = db.get_recipients(active_only=False)
    for recipient in all_recipients:
        if recipient['email_address'].startswith('test'):
            result = db.delete_recipient(recipient['id'])
            print(f"删除 {recipient['email_address']}: {'成功' if result else '失败'}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_email_recipients_management()