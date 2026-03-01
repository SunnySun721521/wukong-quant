import pandas as pd

file_path = r'C:\Users\Sunny Sun\Desktop\邮箱地址.xls'

print("=" * 50)
print("分析Excel文件格式")
print("=" * 50)

try:
    df = pd.read_excel(file_path)
    
    print(f"\n文件读取成功！")
    print(f"行数: {len(df)}")
    print(f"列数: {len(df.columns)}")
    
    print(f"\n列名列表:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. '{col}' (类型: {type(col).__name__})")
    
    print(f"\n前5行数据:")
    print(df.head())
    
    print(f"\n检查是否包含email_address列:")
    print(f"  'email_address' in df.columns: {'email_address' in df.columns}")
    
    print(f"\n检查是否包含邮箱相关列:")
    for col in df.columns:
        if '邮箱' in str(col) or 'email' in str(col).lower() or 'mail' in str(col).lower():
            print(f"  发现相关列: '{col}'")
    
except Exception as e:
    print(f"读取文件失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("分析完成")
print("=" * 50)