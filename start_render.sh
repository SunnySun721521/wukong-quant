#!/bin/bash
# Render 启动脚本
cd backend
python render_start.py
python -c "import app; app.app.run(host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 5006)), debug=False, threaded=True)"
