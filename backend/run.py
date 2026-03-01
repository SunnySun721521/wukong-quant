# -*- coding: utf-8 -*-
import os
import sys

os.chdir(r"D:\trae\备份悟空52224\backend")
os.environ['PYTHONIOENCODING'] = 'utf-8'

if __name__ == '__main__':
    from app import app
    app.run(host='0.0.0.0', port=5006, debug=False, threaded=True)
