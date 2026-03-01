#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render字体下载模块
在Render环境中下载并注册中文字体
"""

import os
import urllib.request

def download_render_fonts():
    """在Render环境中下载中文字体"""
    try:
        import os
        if not (os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_NAME')):
            return False
        
        print("[Render] 开始下载中文字体...")
        
        font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
        
        if not os.path.exists(font_dir):
            os.makedirs(font_dir, exist_ok=True)
        
        font_path = os.path.join(font_dir, 'NotoSansSC-Regular.ttf')
        
        if os.path.exists(font_path) and os.path.getsize(font_path) > 1000000:
            print(f"[Render] 字体已存在: {font_path}")
            return True
        
        font_url = 'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf'
        
        try:
            print(f"[Render] 下载字体: {font_url}")
            urllib.request.urlretrieve(font_url, font_path)
            print(f"[Render] 字体下载完成: {font_path}")
            return True
        except Exception as e:
            print(f"[Render] 下载字体失败: {e}")
            
            fallback_url = 'https://github.com/StellarCN/scp_zh/raw/master/fonts/SimHei.ttf'
            try:
                print(f"[Render] 尝试备用字体: {fallback_url}")
                urllib.request.urlretrieve(fallback_url, font_path)
                print(f"[Render] 备用字体下载完成")
                return True
            except Exception as e2:
                print(f"[Render] 备用字体也下载失败: {e2}")
                return False
        
    except Exception as e:
        print(f"[Render] 字体处理失败: {e}")
        return False

if __name__ == '__main__':
    download_render_fonts()
