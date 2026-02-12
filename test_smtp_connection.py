#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import ssl

def test_smtp_connection():
    """测试SMTP连接"""
    print("=" * 50)
    print("测试SMTP连接")
    print("=" * 50)
    
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    sender_email = "25285603@qq.com"
    sender_auth_code = "63iS$Tj5"
    
    print(f"\nSMTP服务器: {smtp_server}")
    print(f"SMTP端口: {smtp_port}")
    print(f"发送邮箱: {sender_email}")
    print(f"授权码: {sender_auth_code[:3]}***{sender_auth_code[-3:]}")
    
    try:
        print("\n尝试建立SMTP SSL连接...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            print("  ✓ SMTP SSL连接成功")
            
            print("\n尝试登录...")
            server.login(sender_email, sender_auth_code)
            print("  ✓ 登录成功")
            
            print("\n" + "=" * 50)
            print("SMTP连接测试成功！")
            print("=" * 50)
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n  ✗ 认证失败: {e}")
        print("\n可能的原因:")
        print("  1. 授权码不正确")
        print("  2. QQ邮箱的SMTP服务未开启")
        print("  3. 授权码已过期")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"\n  ✗ 连接失败: {e}")
        print("\n可能的原因:")
        print("  1. 网络问题")
        print("  2. SMTP服务器地址或端口不正确")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n  ✗ SMTP错误: {e}")
        return False
        
    except Exception as e:
        print(f"\n  ✗ 未知错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_smtp_connection()
