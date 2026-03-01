#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Dict, Any
from datetime import datetime
from email_config_db import EmailConfigDB

class EmailTemplateEngine:
    """邮件模板引擎类"""
    
    def __init__(self, db_path: str = None):
        self.db = EmailConfigDB(db_path)
        self.templates = self.load_templates()
    
    def load_templates(self) -> Dict[str, Dict[str, str]]:
        """从数据库加载邮件模板"""
        templates = {}
        
        try:
            db_templates = self.db.get_all_templates()
            for template in db_templates:
                template_name = template['template_name']
                templates[template_name] = {
                    'subject': template['subject_template'] or '每日操作计划 - {date}',
                    'body': template['body_template'] or self.get_default_body(template_name)
                }
                print(f"加载邮件模板成功: {template_name}")
        except Exception as e:
            print(f"加载邮件模板失败: {e}")
            # 如果数据库加载失败，使用默认模板
            templates = self.get_default_templates()
        
        return templates
    
    def get_default_body(self, template_name: str) -> str:
        """获取默认邮件正文"""
        if template_name == 'simple':
            return '''尊敬的用户：

您好！

系统已为您生成今日操作计划，请查收附件中的PDF报告。

报告生成时间：{datetime}

如有任何问题，请联系系统管理员。

此致
敬礼！

股票交易管理系统
{datetime}'''
        elif template_name == 'detailed':
            return '''尊敬的用户：

您好！

系统已为您生成今日操作计划，请查收附件中的PDF报告。

【报告摘要】
生成时间：{datetime}
市场状态：{market_status}
当前仓位：{current_position}
总资产：{total_assets}

【报告内容】
1. 市场状态判断
2. 持仓分析
3. 调仓策略
4. 买入策略

【系统信息】
系统名称：股票交易管理系统
版本号：V1.0

如有任何问题，请联系系统管理员。

此致
敬礼！

股票交易管理系统
{datetime}'''
        else:
            return '''尊敬的用户：

您好！

系统已为您生成今日操作计划，请查收附件中的PDF报告。

报告生成时间：{datetime}

如有任何问题，请联系系统管理员。

此致
敬礼！'''
    
    def get_default_templates(self) -> Dict[str, Dict[str, str]]:
        """获取默认模板"""
        return {
            'simple': {
                'subject': '每日操作计划 - {date}',
                'body': self.get_default_body('simple')
            },
            'detailed': {
                'subject': '每日操作计划 - {date}',
                'body': self.get_default_body('detailed')
            }
        }
    
    def render_subject(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """渲染邮件主题"""
        template = self.templates.get(template_name, self.templates.get('simple'))
        subject = template['subject'] if template else '每日操作计划 - {date}'
        
        if context:
            try:
                return subject.format(**context)
            except KeyError as e:
                print(f"渲染邮件主题失败，缺少变量: {e}")
                return subject
        return subject
    
    def render_body(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """渲染邮件正文"""
        template = self.templates.get(template_name, self.templates.get('simple'))
        body = template['body'] if template else self.templates['simple']['body']
        
        if context:
            try:
                return body.format(**context)
            except KeyError as e:
                print(f"渲染邮件正文失败，缺少变量: {e}")
                return body
        return body
    
    def get_available_templates(self) -> Dict[str, str]:
        """获取可用模板列表"""
        return {
            'simple': '简洁版',
            'detailed': '详细版'
        }
    
    def save_template(self, template_name: str, template_type: str, 
                   subject_template: str = None, body_template: str = None, 
                   description: str = None) -> bool:
        """保存邮件模板"""
        try:
            self.db.save_template(template_name, template_type, subject_template, body_template, description)
            # 重新加载模板
            self.templates = self.load_templates()
            return True
        except Exception as e:
            print(f"保存邮件模板失败: {e}")
            return False
    
    def get_template(self, template_name: str) -> Dict[str, Any]:
        """获取指定模板"""
        return self.db.get_template(template_name)