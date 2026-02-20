#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render兼容模块 - 提供Render部署时的数据支持
不影响本地程序运行
"""

import os
import json
import sqlite3
from datetime import datetime

RENDER_EMAIL_CONFIG = {
    'sender_email': '25285603@qq.com',
    'sender_auth_code': 'gyzieuggwgmfbhhh',
    'smtp_server': 'smtp.qq.com',
    'smtp_port': '465',
    'use_ssl': 'true',
    'timeout': '30',
    'retry_times': '3',
    'retry_interval': '5',
    'email_subject_template': '每日操作计划 - {date}',
    'email_body_template': 'simple',
    'recipients': '["lib@tcscd.com"]',
    'enabled': 'true'
}

def is_render_environment():
    """检测是否在Render环境中运行"""
    return os.environ.get('RENDER') is not None or os.environ.get('RENDER_SERVICE_NAME') is not None

def get_data_dir():
    """获取数据目录路径"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def get_strategy_data_dir():
    """获取策略数据目录路径"""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(backend_dir, '..', 'strategy', 'data')

def init_render_email_config():
    """在Render环境中初始化邮箱配置"""
    if not is_render_environment():
        return
    
    try:
        db_path = os.path.join(get_data_dir(), 'email_config.db')
        
        default_config = {
            'sender_email': '25285603@qq.com',
            'sender_auth_code': 'gyzieuggwgmfbhhh',
            'smtp_server': 'smtp.qq.com',
            'smtp_port': '465',
            'use_ssl': 'true',
            'timeout': '30',
            'retry_times': '3',
            'retry_interval': '5',
            'email_subject_template': '每日操作计划 - {date}',
            'email_body_template': 'simple',
            'recipients': '["lib@tcscd.com"]',
            'enabled': 'true'
        }
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            for key, value in default_config.items():
                try:
                    cursor.execute("SELECT config_value FROM email_config WHERE config_key = ?", (key,))
                    result = cursor.fetchone()
                    if result is None:
                        cursor.execute(
                            "INSERT INTO email_config (config_key, config_value, config_type) VALUES (?, ?, 'string')",
                            (key, value)
                        )
                except:
                    pass
            
            conn.commit()
            conn.close()
            print(f"[Render] 邮箱配置已初始化")
    except Exception as e:
        print(f"[Render] 邮箱配置初始化失败: {e}")

def preload_render_data():
    """在Render环境中预加载数据"""
    if not is_render_environment():
        return
    
    print("[Render] 检测到Render环境，预加载数据...")
    
    init_render_email_config()
    preload_stock_data()
    preload_hs300_data()

def preload_stock_data():
    """预加载股票数据到内存缓存"""
    if not is_render_environment():
        return
    
    try:
        import sys
        data_dir = get_strategy_data_dir()
        
        stock_pool_file = os.path.join(data_dir, 'stock_pool.json')
        if os.path.exists(stock_pool_file):
            with open(stock_pool_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[Render] 股票池数据长度: {len(content)} 字符")
        
        position_file = os.path.join(data_dir, 'position_data.csv')
        if os.path.exists(position_file):
            with open(position_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[Render] 持仓数据长度: {len(content)} 字符")
                
    except Exception as e:
        print(f"[Render] 预加载股票数据失败: {e}")

def preload_hs300_data():
    """预加载沪深300数据"""
    if not is_render_environment():
        return
    
    try:
        data_dir = get_strategy_data_dir()
        hs300_file = os.path.join(data_dir, 'hs300_data.csv')
        
        if os.path.exists(hs300_file):
            import pandas as pd
            df = pd.read_csv(hs300_file)
            print(f"[Render] 沪深300数据: {len(df)} 条记录")
    except Exception as e:
        print(f"[Render] 预加载沪深300数据失败: {e}")

if __name__ == '__main__':
    print("Render兼容模块测试")
    print(f"是否Render环境: {is_render_environment()}")
    preload_render_data()
