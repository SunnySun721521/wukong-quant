import pandas as pd
import io

# 创建测试Excel文件
test_data = {
    'email_address': ['test1@example.com', 'test2@example.com', 'test3@example.com'],
    'name': ['测试用户1', '测试用户2', '测试用户3'],
    'description': ['测试邮箱1', '测试邮箱2', '测试邮箱3']
}

df = pd.DataFrame(test_data)

# 保存为Excel文件
output_file = 'test_import_recipients.xlsx'
df.to_excel(output_file, index=False)

print(f"测试文件已创建: {output_file}")
print(f"文件列: {list(df.columns)}")
print(f"文件行数: {len(df)}")

# 测试读取文件
df_read = pd.read_excel(output_file)
print(f"\n读取文件成功")
print(f"列名: {list(df_read.columns)}")
print(f"检查 'email_address' 是否在列中: {'email_address' in df_read.columns}")
print(f"检查 'name' 是否在列中: {'name' in df_read.columns}")
print(f"检查 'description' 是否在列中: {'description' in df_read.columns}")

# 测试遍历数据
print("\n遍历数据:")
for index, row in df_read.iterrows():
    email_address = str(row['email_address']).strip()
    name = str(row.get('name', '')).strip() if 'name' in df_read.columns else None
    description = str(row.get('description', '')).strip() if 'description' in df_read.columns else None
    print(f"  行 {index}: {email_address}, {name}, {description}")