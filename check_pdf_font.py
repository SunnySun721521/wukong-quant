import os
import re

def check_pdf_font(pdf_path):
    """检查PDF文件中使用的字体"""
    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        return
    
    file_size = os.path.getsize(pdf_path)
    print(f"PDF文件: {pdf_path}")
    print(f"文件大小: {file_size:,} 字节")
    print()
    
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
            
        # 检查是否包含中文字体名称
        fonts_found = []
        
        # 检查常见的字体名称
        font_patterns = [
            b'Microsoft YaHei',
            b'msyh',
            b'SimHei',
            b'simhei',
            b'SimSun',
            b'simsun',
            b'Helvetica',
        ]
        
        for pattern in font_patterns:
            if pattern in content:
                fonts_found.append(pattern.decode('utf-8', errors='ignore'))
        
        if fonts_found:
            print("发现的字体:")
            for font in fonts_found:
                print(f"  - {font}")
        else:
            print("未发现特定字体名称")
        
        # 检查PDF是否包含中文内容
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', content.decode('utf-8', errors='ignore'))
        if chinese_chars:
            print(f"\n发现中文字符: {len(chinese_chars)} 个")
            print(f"示例字符: {''.join(chinese_chars[:20])}")
        else:
            print("\n未发现中文字符")
            
        # 检查PDF头
        pdf_header = content[:50]
        print(f"\nPDF文件头: {pdf_header}")
        
    except Exception as e:
        print(f"检查PDF时出错: {e}")

if __name__ == '__main__':
    pdf_path = r'd:\trae\备份悟空52220\test_export.pdf'
    check_pdf_font(pdf_path)