#!/usr/bin/env python3
import sqlite3
import sys
sys.path.insert(0, r'D:\trae\备份悟空52224\backend')

db_path = r'D:\trae\备份悟空52224\backend\data\email_config.db'

print("=" * 60)
print("检查enabled配置")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 查询enabled配置
    cursor.execute("SELECT * FROM email_config WHERE config_key = 'enabled'")
    row = cursor.fetchone()
    
    if row:
        print(f"找到enabled配置:")
        print(f"  ID: {row['id']}")
        print(f"  Key: {row['config_key']}")
        print(f"  Value: {row['config_value']}")
        print(f"  Type: {row['config_type']}")
        print(f"  Description: {row['description']}")
        
        # 测试转换
        value = row['config_value']
        config_type = row['config_type']
        
        if config_type == 'boolean':
            result = value.lower() == 'true'
            print(f"\n转换结果: {result} (类型: {type(result)})")
    else:
        print("❌ 未找到enabled配置")
    
    conn.close()
    
    # 使用EmailConfigDB测试
    print("\n使用EmailConfigDB测试:")
    from email_config_db import EmailConfigDB
    db = EmailConfigDB(db_path)
    config = db.get_all_config()
    print(f"  enabled: {config.get('enabled', 'NOT FOUND')}")
    print(f"  sender_email: {config.get('sender_email', 'NOT FOUND')}")
    
except Exception as e:
    print(f"❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
