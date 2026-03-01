# -*- coding: utf-8 -*-
"""
Render 环境邮件发送模块
确保邮件功能在 Render 环境正常工作
"""
import os
import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

RENDER_ENV = os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_ID')

def is_render_environment():
    """检测是否在 Render 环境"""
    return RENDER_ENV is not None


class RenderEmailSender:
    """Render 环境邮件发送类"""
    
    def __init__(self):
        self.smtp_connection = None
        self.db_path = self._get_db_path()
        self._ensure_db_config()
    
    def _get_db_path(self):
        """获取数据库路径"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, 'email_config.db')
    
    def _ensure_db_config(self):
        """确保数据库配置存在"""
        default_config = {
            'sender_email': '25285603@qq.com',
            'sender_auth_code': 'xqlznzjdrqynbjbc',
            'smtp_server': 'smtp.qq.com',
            'smtp_port': '465',
            'use_ssl': 'true',
            'enabled': 'true',
            'timeout': '60',
            'retry_times': '3',
            'retry_interval': '5'
        }
        
        default_recipients = ['25285603@qq.com', 'lib@tcscd.com']
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_config (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        config_key TEXT UNIQUE NOT NULL,
                        config_value TEXT NOT NULL,
                        config_type TEXT DEFAULT 'string',
                        description TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_recipients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email_address TEXT UNIQUE NOT NULL,
                        is_active INTEGER DEFAULT 1,
                        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_send_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        recipients TEXT,
                        subject TEXT,
                        status TEXT,
                        error_message TEXT,
                        pdf_file TEXT
                    )
                ''')
                
                # 确保配置存在
                for key, value in default_config.items():
                    cursor.execute("SELECT config_value FROM email_config WHERE config_key = ?", (key,))
                    if not cursor.fetchone():
                        config_type = 'boolean' if value.lower() in ['true', 'false'] else 'string'
                        cursor.execute('''
                            INSERT INTO email_config (config_key, config_value, config_type)
                            VALUES (?, ?, ?)
                        ''', (key, value, config_type))
                
                # 确保收件人存在
                for email in default_recipients:
                    cursor.execute('''
                        INSERT OR IGNORE INTO email_recipients (email_address)
                        VALUES (?)
                    ''', (email,))
                
                conn.commit()
                print("[Render] 邮件配置数据库初始化完成")
                
        except Exception as e:
            print(f"[Render] 初始化邮件配置失败: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """获取邮件配置"""
        config = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT config_key, config_value, config_type FROM email_config")
                for row in cursor.fetchall():
                    key, value, config_type = row
                    if config_type == 'boolean':
                        config[key] = value.lower() == 'true'
                    elif config_type == 'integer':
                        config[key] = int(value) if value.isdigit() else 0
                    else:
                        config[key] = value
                
                # 获取收件人
                cursor.execute("SELECT email_address FROM email_recipients WHERE is_active = 1")
                config['recipients'] = [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"[Render] 获取邮件配置失败: {e}")
            config = {
                'sender_email': '25285603@qq.com',
                'sender_auth_code': 'xqlznzjdrqynbjbc',
                'smtp_server': 'smtp.qq.com',
                'smtp_port': 465,
                'use_ssl': True,
                'enabled': True,
                'recipients': ['25285603@qq.com', 'lib@tcscd.com']
            }
        
        return config
    
    def connect_smtp(self, config: Dict[str, Any]) -> bool:
        """建立SMTP连接"""
        try:
            smtp_server = config.get('smtp_server', 'smtp.qq.com')
            smtp_port = int(config.get('smtp_port', 465))
            use_ssl = config.get('use_ssl', True)
            timeout = int(config.get('timeout', 60))
            
            print(f"[Render] 正在连接SMTP: {smtp_server}:{smtp_port}")
            
            if use_ssl:
                self.smtp_connection = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=timeout)
            else:
                self.smtp_connection = smtplib.SMTP(smtp_server, smtp_port, timeout=timeout)
                self.smtp_connection.starttls()
            
            self.smtp_connection.login(config['sender_email'], config['sender_auth_code'])
            print(f"[Render] SMTP连接成功: {smtp_server}:{smtp_port}")
            return True
            
        except Exception as e:
            print(f"[Render] SMTP连接失败: {e}")
            self.smtp_connection = None
            return False
    
    def disconnect_smtp(self):
        """断开SMTP连接"""
        try:
            if self.smtp_connection:
                self.smtp_connection.quit()
                self.smtp_connection = None
                print("[Render] SMTP连接已断开")
        except Exception as e:
            print(f"[Render] 断开SMTP连接失败: {e}")
            self.smtp_connection = None
    
    def send_email(self, pdf_file_path: str, subject: str = None, body: str = None) -> Tuple[bool, Optional[str]]:
        """发送邮件"""
        config = self.get_config()
        
        if not config.get('enabled', True):
            print("[Render] 邮件发送功能未启用")
            return False, "邮件发送功能未启用"
        
        recipients = config.get('recipients', [])
        if not recipients:
            print("[Render] 收件人列表为空")
            return False, "收件人列表为空"
        
        if not os.path.exists(pdf_file_path):
            print(f"[Render] PDF文件不存在: {pdf_file_path}")
            return False, f"PDF文件不存在: {pdf_file_path}"
        
        # 连接SMTP
        if not self.connect_smtp(config):
            return False, "SMTP连接失败"
        
        try:
            # 构建邮件
            msg = MIMEMultipart()
            msg['From'] = config['sender_email']
            msg['To'] = ', '.join(recipients)
            
            # 邮件主题
            if not subject:
                subject = f"每日操作计划 - {datetime.now().strftime('%Y-%m-%d')}"
            msg['Subject'] = subject
            
            # 邮件正文
            if not body:
                body = f"""
您好！

附件是今日的操作计划PDF文件，请查收。

发送时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

祝好！
"""
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添加PDF附件
            with open(pdf_file_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                filename = os.path.basename(pdf_file_path)
                pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                         filename=('utf-8', '', filename))
                msg.attach(pdf_attachment)
            
            # 发送邮件
            self.smtp_connection.send_message(msg)
            
            # 记录日志
            self._log_send(recipients, subject, 'success', None, pdf_file_path)
            
            print(f"[Render] 邮件发送成功: {recipients}")
            return True, None
            
        except Exception as e:
            error_msg = str(e)
            print(f"[Render] 邮件发送失败: {error_msg}")
            self._log_send(recipients, subject or '', 'failed', error_msg, pdf_file_path)
            return False, error_msg
            
        finally:
            self.disconnect_smtp()
    
    def send_test_email(self, recipients: List[str] = None) -> Tuple[bool, Optional[str]]:
        """发送测试邮件"""
        config = self.get_config()
        
        if not recipients:
            recipients = config.get('recipients', [])
        
        if not recipients:
            return False, "收件人列表为空"
        
        # 创建测试PDF
        test_pdf_path = self._create_test_pdf()
        
        if not test_pdf_path:
            return False, "创建测试PDF失败"
        
        subject = f"测试邮件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        body = "这是一封测试邮件，用于验证邮件配置是否正确。"
        
        return self.send_email(test_pdf_path, subject, body)
    
    def _create_test_pdf(self) -> Optional[str]:
        """创建测试PDF文件"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scheduled_pdfs')
            os.makedirs(output_dir, exist_ok=True)
            
            pdf_path = os.path.join(output_dir, f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # 尝试使用中文字体
            font_name = None
            try:
                from render_solution import get_pdf_font_render
                font_name = get_pdf_font_render()
            except:
                pass
            
            if font_name:
                title_style = ParagraphStyle('ChineseTitle', parent=styles['Heading1'], fontName=font_name)
                normal_style = ParagraphStyle('ChineseNormal', parent=styles['Normal'], fontName=font_name)
            else:
                title_style = styles['Heading1']
                normal_style = styles['Normal']
            
            story.append(Paragraph("Test Email", title_style))
            story.append(Paragraph(f"This is a test email.", normal_style))
            story.append(Paragraph(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            
            doc.build(story)
            print(f"[Render] 测试PDF创建成功: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"[Render] 创建测试PDF失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _log_send(self, recipients: List[str], subject: str, status: str, error: str, pdf_file: str):
        """记录发送日志"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO email_send_log (send_time, recipients, subject, status, error_message, pdf_file)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                      ','.join(recipients), subject, status, error, pdf_file))
                conn.commit()
        except Exception as e:
            print(f"[Render] 记录日志失败: {e}")


def send_email_render(pdf_file_path: str, subject: str = None, body: str = None) -> Tuple[bool, Optional[str]]:
    """Render环境发送邮件入口函数"""
    if not is_render_environment():
        return False, "非Render环境"
    
    sender = RenderEmailSender()
    return sender.send_email(pdf_file_path, subject, body)


def send_test_email_render(recipients: List[str] = None) -> Tuple[bool, Optional[str]]:
    """Render环境发送测试邮件入口函数"""
    if not is_render_environment():
        return False, "非Render环境"
    
    sender = RenderEmailSender()
    return sender.send_test_email(recipients)


if __name__ == '__main__':
    print(f"Render环境: {is_render_environment()}")
    
    # 测试发送邮件
    success, error = send_test_email_render()
    print(f"发送结果: {success}, 错误: {error}")
