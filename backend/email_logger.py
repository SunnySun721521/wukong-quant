#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from email_config_db import EmailConfigDB

class EmailLogger:
    """邮件发送日志记录类"""
    
    def __init__(self, db_path: str = None):
        self.db = EmailConfigDB(db_path)
    
    def log_send_success(self, pdf_file: str, recipients: List[str]) -> str:
        """记录发送成功日志"""
        log_id = str(uuid.uuid4())
        recipient_results = [
            {
                'email': recipient,
                'status': 'success'
            }
            for recipient in recipients
        ]
        
        self.db.log_email_send(
            log_id=log_id,
            pdf_file=pdf_file,
            status='success',
            recipients=recipient_results
        )
        
        print(f"记录邮件发送成功日志: {log_id}")
        return log_id
    
    def log_send_failure(self, pdf_file: str, recipients: List[str], error_type: str, error_message: str, 
                        recipient_results: List[Dict[str, Any]] = None, retry_count: int = 0, 
                        retry_details: List[Dict[str, Any]] = None) -> str:
        """记录发送失败日志"""
        log_id = str(uuid.uuid4())
        
        if recipient_results is None:
            recipient_results = [
                {
                    'email': recipient,
                    'status': 'failure',
                    'error_message': error_message
                }
                for recipient in recipients
            ]
        
        self.db.log_email_send(
            log_id=log_id,
            pdf_file=pdf_file,
            status='failure',
            recipients=recipient_results,
            error_message=error_message,
            retry_count=retry_count
        )
        
        print(f"记录邮件发送失败日志: {log_id}")
        return log_id
    
    def get_send_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取发送日志"""
        return self.db.get_email_logs(limit)
    
    def get_send_statistics(self) -> Dict[str, Any]:
        """获取发送统计信息"""
        logs = self.get_send_logs(1000)  # 获取更多日志用于统计
        
        total_logs = len(logs)
        success_logs = [log for log in logs if log['status'] == 'success']
        failure_logs = [log for log in logs if log['status'] == 'failure']
        
        total_recipients = sum(len(log['recipients']) for log in logs)
        success_recipients = sum(
            len([r for r in log['recipients'] if r['status'] == 'success'])
            for log in logs
        )
        failure_recipients = total_recipients - success_recipients
        
        return {
            'total_logs': total_logs,
            'success_logs': len(success_logs),
            'failure_logs': len(failure_logs),
            'total_recipients': total_recipients,
            'success_recipients': success_recipients,
            'failure_recipients': failure_recipients,
            'success_rate': (success_recipients / total_recipients * 100) if total_recipients > 0 else 0
        }