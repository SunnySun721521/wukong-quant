from flask import Flask, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api/plan/market-status', methods=['GET'])
def get_market_status():
    print("API called: /api/plan/market-status")
    
    # 模拟市场状态数据
    is_bull = True
    
    # 模拟数据
    hs300_index = 3850.23
    hs300_change = 1.23
    ma120 = 3760.50
    
    result = {
        "status": "bull" if is_bull else "bear",
        "status_text": "牛市" if is_bull else "熊市",
        "position_suggestion": "80%" if is_bull else "30%",
        "hs300_index": hs300_index,
        "hs300_change": hs300_change,
        "ma120": ma120,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "chart_data": {
            "labels": ["1月20日", "1月21日", "1月22日", "1月23日", "1月24日", "1月25日", "1月26日"],
            "hs300": [3750, 3780, 3760, 3800, 3820, 3810, hs300_index],
            "ma120": [3700, 3710, 3720, 3730, 3740, 3750, ma120]
        }
    }
    
    return jsonify(result)

if __name__ == '__main__':
    print("测试服务器启动中...")
    print("注册的路由:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule}")
    app.run(host='0.0.0.0', port=5007, debug=True)
