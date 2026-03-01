# -*- coding: utf-8 -*-
from flask import Flask, jsonify
import os
import csv
from datetime import datetime

app = Flask(__name__)

def get_position_file_path():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'strategy', 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'position_data.csv')

@app.route('/api/plan/adjustment', methods=['GET'])
def get_adjustment_strategy():
    print("=" * 60)
    print("API called: /api/plan/adjustment")
    print("=" * 60)
    
    try:
        position_file = get_position_file_path()
        print(f"持仓文件路径: {position_file}")
        print(f"文件是否存在: {os.path.exists(position_file)}")
        positions = []
        
        if os.path.exists(position_file):
            print(f"从本地文件读取持仓数据: {position_file}")
            try:
                with open(position_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    positions = list(reader)
            except Exception as e:
                print(f"读取文件失败: {e}")
                import traceback
                traceback.print_exc()
                positions = []
        
        print(f"读取到 {len(positions)} 条持仓记录")
        
        suggestions = []
        
        for pos in positions:
            try:
                symbol = pos.get('symbol', '')
                name = pos.get('name', symbol)
                current_price = float(pos.get('current_price', 0))
                profit_loss_percent = float(pos.get('profit_loss_percent', 0))
                
                if profit_loss_percent >= 10:
                    suggestions.append({
                        "action": "sell",
                        "action_text": "止盈",
                        "symbol": symbol,
                        "name": name,
                        "current_price": current_price,
                        "reason": f"当前盈利{profit_loss_percent:.2f}%，达到止盈条件",
                        "detail": "建议卖出部分仓位，锁定收益"
                    })
                elif profit_loss_percent <= -4:
                    suggestions.append({
                        "action": "sell",
                        "action_text": "止损",
                        "symbol": symbol,
                        "name": name,
                        "current_price": current_price,
                        "reason": f"当前亏损{abs(profit_loss_percent):.2f}%，达到止损条件",
                        "detail": "建议严格执行止损，避免更大损失"
                    })
            except Exception as e:
                print(f"处理持仓 {pos.get('symbol')} 失败: {e}")
        
        print(f"生成 {len(suggestions)} 条调仓建议")
        
        result = {
            "rules": [
                {"type": "止盈规则", "description": "盈利达到10%时，触发止盈建议"},
                {"type": "止损规则", "description": "亏损达到4%时，触发止损建议，严格执行"}
            ],
            "suggestions": suggestions,
            "update_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"返回结果: {len(suggestions)} 条建议")
        return jsonify(result)
        
    except Exception as e:
        print(f"获取调仓策略失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=False)
