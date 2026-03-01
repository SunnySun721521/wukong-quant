#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试app导入
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("测试导入app...")
try:
    import app
    print("✅ app导入成功")
    print(f"app模块属性: {dir(app)}")
except Exception as e:
    print(f"❌ app导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成")
