import smtplib
import ssl
import socket

print("=" * 50)
print("测试SMTP连接 (完整错误信息)")
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
    
    # 获取服务器响应
    response = server.noop()
    print(f"服务器响应: {response}")
    
    # 设置调试模式
    server.set_debuglevel(2)
    
    # 尝试登录
    print(f"尝试登录: {sender_email}")
    print(f"授权码长度: {len(sender_auth_code)}")
    
    try:
        server.login(sender_email, sender_auth_code)
        print("登录成功")
    except smtplib.SMTPAuthenticationError as e:
        print(f"认证失败: {e}")
        print(f"错误代码: {e.smtp_code}")
        print(f"错误消息: {e.smtp_error}")
        print("\n可能的原因:")
        print("1. 授权码不正确")
        print("2. QQ邮箱未开启SMTP服务")
        print("3. 授权码已过期")
        print("4. 邮箱账号被限制")
        
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
    
except socket.timeout as e:
    print(f"连接超时: {e}")
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