import sqlite3
import os

# 查询邮件配置数据库
def query_email_config():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'email_config.db')
    
    if not os.path.exists(db_path):
        print("邮件配置数据库不存在")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 查询邮件配置
        print("=== 邮件配置 ===")
        cursor.execute("SELECT config_key, config_value FROM email_config")
        configs = cursor.fetchall()
        for key, value in configs:
            print(f"{key}: {value}")
        
        # 查询最新的邮件发送日志
        print("\n=== 最新的邮件发送日志 ===")
        cursor.execute("""
            SELECT log_id, created_at, pdf_file, status, error_message 
            FROM email_send_log 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        logs = cursor.fetchall()
        for log_id, timestamp, pdf_file, status, error_message in logs:
            print(f"时间: {timestamp}")
            print(f"状态: {status}")
            print(f"PDF文件: {pdf_file}")
            if error_message:
                print(f"错误信息: {error_message}")
            print("-" * 50)

if __name__ == "__main__":
    query_email_config()