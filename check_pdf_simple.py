import os

pdf_path = r'd:\trae\备份悟空52220\test_export.pdf'
if os.path.exists(pdf_path):
    file_size = os.path.getsize(pdf_path)
    print(f"PDF文件存在: {pdf_path}")
    print(f"文件大小: {file_size:,} 字节")
    
    with open(pdf_path, 'rb') as f:
        content = f.read()
    
    print(f"PDF头: {content[:50]}")
    
    if b'msyh' in content:
        print("发现中文字体: msyh")
    elif b'Helvetica' in content:
        print("发现字体: Helvetica")
    else:
        print("未发现特定字体")
else:
    print(f"PDF文件不存在: {pdf_path}")