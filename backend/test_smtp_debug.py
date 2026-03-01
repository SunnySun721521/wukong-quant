import smtplib
import ssl

print("=" * 50)
print("测试SMTP连接 (详细错误信息)")
print("=" * 50)

# SMTP配置
smtp_server = "smtp.qq.com"
smtp_port = 465
sender_email = "25285603@qq.com"
sender_auth_code = "xhjsjgjxkbcbbjdh"

print(f"\n尝试连接到 {smtp_server}:{smtp_port}...")

try:
    # 使用SSL连接
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=30)
    print("SSL连接成功")
    
    # 设置调试模式
    server.set_debuglevel(2)
    
    # 登录
    print(f"尝试登录: {sender_email}")
    server.login(sender_email, sender_auth_code)
    print("登录成功")
    
    # 发送测试邮件
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.header import Header
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = "lib@tcscd.com"
    msg['Subject'] = Header("测试邮件", 'utf-8')
    
    body = "这是一封测试邮件，用于验证SMTP连接。"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    server.send_message(msg)
    print("邮件发送成功")
    
    server.quit()
    
except smtplib.SMTPAuthenticationError as e:
    print(f"认证失败: {e}")
    print(f"错误代码: {e.smtp_code}")
    print(f"错误消息: {e.smtp_error}")
except smtplib.SMTPException as e:
    print(f"SMTP错误: {e}")
    if hasattr(e, 'smtp_code'):
        print(f"错误代码: {e.smtp_code}")
    if hasattr(e, 'smtp_error'):
        print(f"错误消息: {e.smtp_error}")
except Exception as e:
    print(f"连接失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)