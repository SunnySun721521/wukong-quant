# -*- coding: utf-8 -*-
"""
Render 环境 PDF 字体处理模块
确保 PDF 中文正确显示
"""
import os
import subprocess

RENDER_ENV = os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_ID')

def is_render_environment():
    """检测是否在 Render 环境"""
    return RENDER_ENV is not None


def get_chinese_font():
    """获取中文字体 - Render环境专用"""
    if not is_render_environment():
        return None
    
    print("[Render] 开始获取中文字体...")
    
    # 尝试注册系统字体
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        print("[Render] reportlab未安装")
        return None
    
    # 方法1: 尝试使用系统已安装的中文字体
    system_fonts = find_system_chinese_fonts()
    for font_path, font_name in system_fonts:
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            print(f"[Render] 成功注册系统字体: {font_name} @ {font_path}")
            return font_name
        except Exception as e:
            print(f"[Render] 注册字体失败 {font_name}: {e}")
            continue
    
    # 方法2: 使用内置的reportlab字体（不支持中文，但至少不会报错）
    print("[Render] 警告: 未找到可用的中文字体，PDF中文可能无法正常显示")
    return None


def find_system_chinese_fonts():
    """查找系统中的中文字体"""
    fonts = []
    
    # Render环境可能的字体路径
    possible_paths = [
        # DejaVu 字体 (通常预装)
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans.ttf',
        # Noto 字体
        '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
        '/usr/share/fonts/noto/NotoSans-Regular.ttf',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        # Liberation 字体
        '/usr/share/fonts/liberation/LiberationSans-Regular.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        # WenQuanYi 字体
        '/usr/share/fonts/wenquanyi/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        # Source Han 字体
        '/usr/share/fonts/adobe-source-han-sans/SourceHanSansCN-Regular.otf',
        # FreeFont
        '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
        # 其他常见路径
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            font_name = os.path.basename(path).split('.')[0].replace('-', '').replace('_', '')
            fonts.append((path, font_name))
            print(f"[Render] 发现系统字体: {font_name} @ {path}")
    
    # 尝试使用fc-list命令查找中文字体
    try:
        result = subprocess.run(['fc-list', ':lang=zh'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(':')
                    if parts:
                        font_path = parts[0].strip()
                        if os.path.exists(font_path):
                            font_name = f"zh_{len(fonts)}"
                            fonts.append((font_path, font_name))
                            print(f"[Render] fc-list发现中文字体: {font_path}")
    except Exception as e:
        print(f"[Render] fc-list查找失败: {e}")
    
    return fonts


def register_font_for_pdf():
    """为PDF注册字体 - 返回字体名称供PDF使用"""
    font = get_chinese_font()
    if font:
        return font
    
    # 如果没有找到中文字体，尝试使用reportlab内置字体
    # 这些字体不支持中文，但可以防止PDF生成失败
    return 'Helvetica'


if __name__ == '__main__':
    print(f"Render环境: {is_render_environment()}")
    fonts = find_system_chinese_fonts()
    print(f"发现的字体: {fonts}")
    font = get_chinese_font()
    print(f"使用的字体: {font}")
