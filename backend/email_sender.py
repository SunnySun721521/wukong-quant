#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from email_config_manager import EmailConfigManager
from email_template_engine import EmailTemplateEngine
from email_logger import EmailLogger

class EmailSender:
    """邮件发送类"""
    
    def __init__(self, config_manager: EmailConfigManager = None, 
                 template_engine: EmailTemplateEngine = None,
                 logger: EmailLogger = None):
        self.config_manager = config_manager or EmailConfigManager()
        self.template_engine = template_engine or EmailTemplateEngine()
        self.logger = logger or EmailLogger()
        self.smtp_connection = None
    
    def send_email(self, pdf_file_path: str, market_data: Dict[str, Any] = None) -> tuple[bool, Optional[str]]:
        """发送邮件（主方法）"""
        config = self.config_manager.get_config()
        
        if not config.get('enabled', False):
            print("邮件发送功能未启用")
            return True, None
        
        is_valid, error_msg = self.config_manager.validate_config()
        if not is_valid:
            print(f"邮件配置验证失败: {error_msg}")
            self.logger.log_send_failure(
                pdf_file=pdf_file_path,
                recipients=config.get('recipients', []),
                error_type='config_error',
                error_message=error_msg
            )
            return False, error_msg
        
        if not os.path.exists(pdf_file_path):
            error_msg = f"PDF文件不存在: {pdf_file_path}"
            print(error_msg)
            self.logger.log_send_failure(
                pdf_file=pdf_file_path,
                recipients=config.get('recipients', []),
                error_type='file_error',
                error_message=error_msg
            )
            return False, error_msg
        
        try:
            context = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'datetime': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            }
            
            if market_data:
                context.update(market_data)
            
            subject = self.template_engine.render_subject(
                config.get('email_body_template', 'simple'),
                context
            )
            body = self.template_engine.render_body(
                config.get('email_body_template', 'simple'),
                context
            )
            
            recipients = config.get('recipients', [])
            retry_times = config.get('retry_times', 3)
            retry_interval = config.get('retry_interval', 5)
            
            success, error_msg, recipient_results = self.retry_send(
                subject, body, pdf_file_path, recipients, 
                retry_times, retry_interval, config
            )
            
            if success:
                self.logger.log_send_success(pdf_file_path, recipients)
                return True, None
            else:
                self.logger.log_send_failure(
                    pdf_file=pdf_file_path,
                    recipients=recipients,
                    error_type='send_error',
                    error_message=error_msg,
                    recipient_results=recipient_results,
                    retry_count=retry_times
                )
                return False, error_msg
            
        except Exception as e:
            error_msg = f"发送邮件异常: {str(e)}"
            print(error_msg)
            self.logger.log_send_failure(
                pdf_file=pdf_file_path,
                recipients=config.get('recipients', []),
                error_type='exception',
                error_message=error_msg
            )
            return False, error_msg
    
    def retry_send(self, subject: str, body: str, pdf_file_path: str, 
                  recipients: List[str], retry_times: int, retry_interval: int,
                  config: Dict[str, Any]) -> tuple[bool, Optional[str], List[Dict[str, Any]]]:
        """重试发送机制"""
        retry_details = []
        recipient_results = []
        
        for attempt in range(retry_times + 1):
            print(f"尝试发送邮件 (第 {attempt + 1}/{retry_times + 1} 次)")
            
            try:
                if attempt > 0:
                    time.sleep(retry_interval * (2 ** (attempt - 1)))
                
                if not self.smtp_connection:
                    if not self.connect_smtp(config):
                        error_msg = "SMTP连接失败"
                        retry_details.append({
                            'retry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'error_type': 'connection_error',
                            'error_message': error_msg
                        })
                        if attempt < retry_times:
                            print(f"等待 {retry_interval * (2 ** attempt)} 秒后重试...")
                        continue
                
                success, error_msg, results = self._send_to_recipients(
                    subject, body, pdf_file_path, recipients, config
                )
                
                if success:
                    return True, None, results
                else:
                    retry_details.append({
                        'retry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'error_type': 'send_error',
                        'error_message': error_msg
                    })
                    recipient_results = results
                    
            except Exception as e:
                error_msg = str(e)
                print(f"发送邮件失败 (第 {attempt + 1} 次): {error_msg}")
                retry_details.append({
                    'retry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'error_type': 'exception',
                    'error_message': error_msg
                })
            
            if attempt < retry_times:
                print(f"等待 {retry_interval * (2 ** attempt)} 秒后重试...")
        
        return False, "重试次数已用尽，发送失败", recipient_results
    
    def _send_to_recipients(self, subject: str, body: str, pdf_file_path: str,
                           recipients: List[str], config: Dict[str, Any]) -> tuple[bool, Optional[str], List[Dict[str, Any]]]:
        """发送邮件给所有接收人"""
        results = []
        success_count = 0
        
        for recipient in recipients:
            try:
                msg = MIMEMultipart()
                msg['From'] = config['sender_email']
                msg['To'] = recipient
                msg['Subject'] = subject
                
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
                
                with open(pdf_file_path, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    filename = os.path.basename(pdf_file_path)
                    pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                           filename=('utf-8', '', filename))
                    msg.attach(pdf_attachment)
                
                self.smtp_connection.send_message(msg)
                
                results.append({
                    'email': recipient,
                    'status': 'success'
                })
                success_count += 1
                print(f"发送邮件成功: {recipient}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"发送邮件失败: {recipient}, 错误: {error_msg}")
                results.append({
                    'email': recipient,
                    'status': 'failure',
                    'error_message': error_msg
                })
        
        if success_count == len(recipients):
            return True, None, results
        elif success_count > 0:
            return False, f"部分发送成功 ({success_count}/{len(recipients)})", results
        else:
            return False, "所有发送均失败", results
    
    def connect_smtp(self, config: Dict[str, Any]) -> bool:
        """建立SMTP连接"""
        try:
            smtp_server = config.get('smtp_server', 'smtp.qq.com')
            smtp_port = config.get('smtp_port', 465)
            use_ssl = config.get('use_ssl', True)
            timeout = config.get('timeout', 30)
            
            if use_ssl:
                self.smtp_connection = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=timeout)
            else:
                self.smtp_connection = smtplib.SMTP(smtp_server, smtp_port, timeout=timeout)
                self.smtp_connection.starttls()
            
            self.smtp_connection.login(config['sender_email'], config['sender_auth_code'])
            print(f"SMTP连接成功: {smtp_server}:{smtp_port}")
            return True
            
        except Exception as e:
            error_msg = f"SMTP连接失败: {str(e)}"
            print(error_msg)
            self.smtp_connection = None
            return False
    
    def disconnect_smtp(self):
        """断开SMTP连接"""
        try:
            if self.smtp_connection:
                self.smtp_connection.quit()
                self.smtp_connection = None
                print("SMTP连接已断开")
        except Exception as e:
            print(f"断开SMTP连接失败: {e}")
            self.smtp_connection = None