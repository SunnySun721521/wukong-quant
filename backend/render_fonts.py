#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render字体支持模块
在Render环境中提供可用的中文字体
"""

import os

def get_render_font_path():
    """获取Render可用的中文字体路径"""
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    
    if not os.path.exists(font_dir):
        os.makedirs(font_dir, exist_ok=True)
    
    font_path = os.path.join(font_dir, 'NotoSansSC-Regular.ttf')
    
    if not os.path.exists(font_path):
        print(f"[Render] 字体文件不存在: {font_path}")
        return None
    
    return font_path

def register_render_fonts():
    """在Render环境中注册字体"""
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        font_path = get_render_font_path()
        
        if font_path and os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('NotoSansSC', font_path))
            print(f"[Render] 成功注册字体: NotoSansSC")
            return 'NotoSansSC'
        
        print("[Render] 未找到可用字体，尝试使用内置字体")
        return 'Helvetica'
        
    except Exception as e:
        print(f"[Render] 注册字体失败: {e}")
        return None

def get_render_chinese_font():
    """获取Render可用的中文字体名称"""
    try:
        font_name = register_render_fonts()
        return font_name if font_name else 'Helvetica'
    except Exception as e:
        print(f"[Render] 获取字体失败: {e}")
        return 'Helvetica'
