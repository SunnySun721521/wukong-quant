# -*- coding: utf-8 -*-
"""
Render 环境 PDF 字体处理模块
确保 PDF 中文正确显示
"""
import os
import urllib.request

RENDER_ENV = os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_ID')

def is_render_environment():
    """检测是否在 Render 环境"""
    return RENDER_ENV is not None


def get_chinese_font():
    """获取中文字体"""
    if not is_render_environment():
        return None
    
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    os.makedirs(font_dir, exist_ok=True)
    
    # 尝试多种字体路径
    font_paths = [
        # Noto CJK 字体
        ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 'NotoSansCJK'),
        ('/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc', 'NotoSansCJK'),
        ('/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc', 'NotoSansCJK'),
        # WenQuanYi 字体
        ('/usr/share/fonts/wenquanyi/wenquanyi/wqy-zenhei.ttc', 'WQYZenHei'),
        ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 'WQYZenHei'),
        # Source Han 字体
        ('/usr/share/fonts/adobe-source-han-sans/SourceHanSansCN-Regular.otf', 'SourceHanSans'),
    ]
    
    # 尝试注册系统字体
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        for font_path, font_name in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"[Render] 成功注册系统字体: {font_name}")
                    return font_name
                except Exception as e:
                    print(f"[Render] 注册字体失败 {font_name}: {e}")
                    continue
    except Exception as e:
        print(f"[Render] 字体注册模块导入失败: {e}")
    
    # 下载字体
    downloaded_font = download_chinese_font()
    if downloaded_font:
        return downloaded_font
    
    print("[Render] 警告: 未找到可用的中文字体")
    return None


def download_chinese_font():
    """下载中文字体"""
    if not is_render_environment():
        return None
    
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    os.makedirs(font_dir, exist_ok=True)
    
    # 使用 Noto Sans SC (简体中文)
    font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf"
    font_path = os.path.join(font_dir, 'NotoSansSC-Regular.otf')
    
    if os.path.exists(font_path):
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            pdfmetrics.registerFont(TTFont('NotoSansSC', font_path))
            print(f"[Render] 使用已下载的字体: NotoSansSC")
            return 'NotoSansSC'
        except Exception as e:
            print(f"[Render] 注册已下载字体失败: {e}")
    
    # 下载字体
    try:
        print(f"[Render] 正在下载中文字体...")
        urllib.request.urlretrieve(font_url, font_path)
        print(f"[Render] 字体下载成功: {font_path}")
        
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        pdfmetrics.registerFont(TTFont('NotoSansSC', font_path))
        print(f"[Render] 成功注册下载字体: NotoSansSC")
        return 'NotoSansSC'
        
    except Exception as e:
        print(f"[Render] 下载字体失败: {e}")
        
        # 尝试备用字体URL
        backup_urls = [
            "https://raw.githubusercontent.com/ArtifexSoftware/urw-base35-fonts/master/fonts/NimbusRoman-Regular.otf",
        ]
        
        for url in backup_urls:
            try:
                backup_path = os.path.join(font_dir, 'backup_font.otf')
                urllib.request.urlretrieve(url, backup_path)
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
                pdfmetrics.registerFont(TTFont('BackupFont', backup_path))
                print(f"[Render] 使用备用字体: BackupFont")
                return 'BackupFont'
            except:
                continue
    
    return None


def create_pdf_with_chinese(filename, content_list):
    """创建包含中文的PDF"""
    if not is_render_environment():
        return None
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        font_name = get_chinese_font()
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        if font_name:
            title_style = ParagraphStyle('ChineseTitle', parent=styles['Heading1'], fontName=font_name)
            normal_style = ParagraphStyle('ChineseNormal', parent=styles['Normal'], fontName=font_name)
        else:
            title_style = styles['Heading1']
            normal_style = styles['Normal']
        
        for item in content_list:
            if item.get('type') == 'title':
                story.append(Paragraph(item.get('text', ''), title_style))
            elif item.get('type') == 'paragraph':
                story.append(Paragraph(item.get('text', ''), normal_style))
            elif item.get('type') == 'spacer':
                story.append(Spacer(1, item.get('height', 12)))
        
        doc.build(story)
        print(f"[Render] PDF创建成功: {filename}")
        return filename
        
    except Exception as e:
        print(f"[Render] 创建PDF失败: {e}")
        return None


if __name__ == '__main__':
    print(f"Render环境: {is_render_environment()}")
    font = get_chinese_font()
    print(f"中文字体: {font}")
