# -*- coding: utf-8 -*-
"""
Render 环境启动脚本
确保所有配置和数据正确初始化
"""
import os
import sys

# 设置环境变量
os.environ['RENDER'] = 'true'

# 添加backend目录到路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

print("[Render] 启动脚本开始执行...")
print(f"[Render] Python版本: {sys.version}")
print(f"[Render] 工作目录: {os.getcwd()}")
print(f"[Render] Backend目录: {backend_dir}")

# 确保数据目录存在
data_dir = os.path.join(backend_dir, 'data')
os.makedirs(data_dir, exist_ok=True)
print(f"[Render] 数据目录: {data_dir}")

# 初始化邮箱配置数据库
try:
    print("[Render] 初始化邮箱配置...")
    import sqlite3
    
    db_path = os.path.join(data_dir, 'email_config.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建配置表
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
    
    # 创建收件人表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_address TEXT UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 确保默认配置存在
    default_configs = [
        ('sender_email', '25285603@qq.com', 'string'),
        ('sender_auth_code', 'xqlznzjdrqynbjbc', 'string'),
        ('smtp_server', 'smtp.qq.com', 'string'),
        ('smtp_port', '465', 'string'),
        ('use_ssl', 'true', 'boolean'),
        ('enabled', 'true', 'boolean'),
        ('timeout', '60', 'integer'),
        ('retry_times', '3', 'integer'),
        ('retry_interval', '5', 'integer'),
    ]
    
    for key, value, config_type in default_configs:
        cursor.execute("SELECT config_value FROM email_config WHERE config_key = ?", (key,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO email_config (config_key, config_value, config_type) VALUES (?, ?, ?)",
                (key, value, config_type)
            )
    
    # 确保默认收件人存在
    default_recipients = ['25285603@qq.com', 'lib@tcscd.com']
    for email in default_recipients:
        cursor.execute(
            "INSERT OR IGNORE INTO email_recipients (email_address) VALUES (?)",
            (email,)
        )
    
    conn.commit()
    conn.close()
    print("[Render] 邮箱配置初始化完成")
    
except Exception as e:
    print(f"[Render] 邮箱配置初始化失败: {e}")

# 导入app模块（这会触发app.py中的初始化代码）
print("[Render] 导入Flask应用...")
import app

# 启动Flask服务（调用app.py中的run_app函数）
print("[Render] 启动Flask服务...")
app.run_app()
