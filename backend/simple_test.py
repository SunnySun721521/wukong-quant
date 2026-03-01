# -*- coding: utf-8 -*-
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/plan/adjustment', methods=['GET'])
def get_adjustment_strategy():
    return jsonify({
        "rules": [{"type": "测试", "description": "测试数据"}],
        "suggestions": [
            {"action": "sell", "action_text": "止损", "symbol": "300308", "name": "中际旭创", "reason": "测试数据"}
        ],
        "update_time": "2026-02-26 14:10:00"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=False)
