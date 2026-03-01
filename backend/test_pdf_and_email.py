import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app

print("=" * 50)
print("手动测试PDF导出和邮件发送")
print("=" * 50)

# 使用Flask测试客户端
with app.app.test_client() as client:
    # 1. 手动触发PDF导出
    print("\n1. 手动触发PDF导出:")
    response = client.post('/api/plan/export-pdf')
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.get_json()
        print(f"  响应: {data}")
        
        if data.get('success'):
            pdf_file = data.get('pdf_file')
            print(f"  PDF文件: {pdf_file}")
            
            # 2. 检查PDF文件是否存在
            if pdf_file and os.path.exists(pdf_file):
                print(f"  PDF文件存在")
                
                # 3. 手动触发邮件发送
                print("\n2. 手动触发邮件发送:")
                try:
                    result = app._send_email_notification(pdf_file)
                    print(f"  邮件发送结果: {result}")
                except Exception as e:
                    print(f"  邮件发送失败: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"  PDF文件不存在")
        else:
            print(f"  PDF导出失败: {data.get('error')}")
    else:
        print(f"  请求失败")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)