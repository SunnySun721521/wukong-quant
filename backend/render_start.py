#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render专用启动脚本
不影响本地程序运行
用于 Render 部署时自动初始化数据
"""

import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

os.environ['RENDER'] = '1'

try:
    import render_settings
    render_settings.apply_render_patches()
except ImportError:
    print("render_settings模块未找到，跳过Render修补")

try:
    import render_compat
    render_compat.preload_render_data()
except ImportError:
    print("render_compat模块未找到，跳过Render初始化")

try:
    import render_data
    render_data.patch_data_providers()
except ImportError:
    print("render_data模块未找到，跳过数据修补")

if __name__ == '__main__':
    import app
    app.run_app()
