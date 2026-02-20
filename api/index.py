import sys
import os

vercel_mode = True
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import csv
import time
import random
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backup_data')
STOCK_POOL_FILE = os.path.join(DATA_DIR, 'stock_pool.json')
POSITION_FILE = os.path.join(DATA_DIR, 'positions.csv')

app.config['JSON_AS_ASCII'] = False

try:
    import baostock as bs
    BS_AVAILABLE = True
except ImportError:
    BS_AVAILABLE = False
    print("baostock not available")

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("reportlab not available")

stock_pool_manager = None
try:
    class StockPoolManager:
        def __init__(self):
            self.current_pool = ['600519', '000858', '002371']
            self._load_pool()
        
        def _load_pool(self):
            if os.path.exists(STOCK_POOL_FILE):
                try:
                    with open(STOCK_POOL_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.current_pool = data.get('stocks', self.current_pool)
                except:
                    pass
    
    stock_pool_manager = StockPoolManager()
except Exception as e:
    stock_pool_manager = type('obj', (object,), {'current_pool': ['600519', '000858', '002371']})()

def get_position_file_path():
    return POSITION_FILE

def get_stock_pool_manager():
    return stock_pool_manager

@app.route('/')
def index():
    return send_file(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web', 'index.html'))

@app.route('/<path:path>')
def serve_static(path):
    static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web', path)
    if os.path.exists(static_path):
        return send_file(static_path)
    return "Not Found", 404

@app.route('/api/home/overview', methods=['GET'])
def get_home_overview():
    if not BS_AVAILABLE:
        return jsonify({"error": "baostock not available"})
    
    try:
        import baostock as bs
        lg = bs.login()
        if lg.error_code != '0':
            return jsonify({"error": "baostock login failed"})
        
        try:
            stock_pool = get_stock_pool_manager().current_pool
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = "2026-01-01"
            
            holdings = []
            total_value = 0
            total_cost = 0
            
            if os.path.exists(POSITION_FILE):
                with open(POSITION_FILE, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for pos in reader:
                        symbol = pos['symbol']
                        quantity = int(pos['quantity'])
                        cost_price = float(pos['cost_price'])
                        
                        bs_code = f"sh.{symbol}" if symbol.startswith('6') else f"sz.{symbol}"
                        rs = bs.query_history_k_data_plus(bs_code, "date,close", start_date=start_date, end_date=end_date, frequency="d")
                        
                        current_price = cost_price
                        if rs.error_code == '0' and rs.next():
                            data = rs.get_row_data()
                            if len(data) >= 2:
                                current_price = float(data[1])
                        
                        value = quantity * current_price
                        cost = quantity * cost_price
                        
                        holdings.append({
                            "symbol": symbol,
                            "name": symbol,
                            "quantity": quantity,
                            "cost_price": cost_price,
                            "current_price": current_price,
                            "value": value,
                            "profit": value - cost,
                            "profit_rate": (value - cost) / cost * 100 if cost > 0 else 0
                        })
                        
                        total_value += value
                        total_cost += cost
            
            initial_capital = 200000
            final_value = total_value if total_value > 0 else initial_capital
            total_return = final_value - initial_capital
            total_return_rate = (total_return / initial_capital) * 100 if initial_capital > 0 else 0
            
            return jsonify({
                "initial_capital": initial_capital,
                "final_value": round(final_value, 2),
                "total_return": round(total_return, 2),
                "total_return_rate": round(total_return_rate, 2),
                "max_drawdown": 0,
                "holdings": holdings,
                "start_date": start_date,
                "end_date": datetime.now().strftime("%Y-%m-%d")
            })
        finally:
            bs.logout()
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/stock/kline', methods=['GET'])
def get_stock_kline():
    symbol = request.args.get('symbol', '')
    if not symbol:
        return jsonify({"error": "symbol required"})
    
    if not BS_AVAILABLE:
        return jsonify({"error": "baostock not available"})
    
    try:
        import baostock as bs
        lg = bs.login()
        if lg.error_code != '0':
            return jsonify({"error": "baostock login failed"})
        
        try:
            bs_code = f"sh.{symbol}" if symbol.startswith('6') else f"sz.{symbol}"
            rs = bs.query_history_k_data_plus(bs_code, "date,open,high,low,close,volume", start_date="2020-01-01", end_date=datetime.now().strftime("%Y-%m-%d"), frequency="d")
            
            data = []
            if rs.error_code == '0':
                while rs.next():
                    row = rs.get_row_data()
                    data.append({
                        "date": row[0],
                        "open": float(row[1]),
                        "high": float(row[2]),
                        "low": float(row[3]),
                        "close": float(row[4]),
                        "volume": float(row[5])
                    })
            
            return jsonify({"data": data})
        finally:
            bs.logout()
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/stock_pool', methods=['GET', 'POST'])
def stock_pool_api():
    if request.method == 'GET':
        return jsonify({"stocks": get_stock_pool_manager().current_pool})
    
    if request.method == 'POST':
        data = request.get_json()
        stocks = data.get('stocks', [])
        try:
            with open(STOCK_POOL_FILE, 'w', encoding='utf-8') as f:
                json.dump({"stocks": stocks}, f, ensure_ascii=False)
            get_stock_pool_manager().current_pool = stocks
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)})

@app.route('/api/position', methods=['GET', 'POST', 'DELETE'])
def position_api():
    if request.method == 'GET':
        positions = []
        if os.path.exists(POSITION_FILE):
            with open(POSITION_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    positions.append(row)
        return jsonify({"positions": positions})
    
    if request.method == 'POST':
        data = request.get_json()
        positions = []
        if os.path.exists(POSITION_FILE):
            with open(POSITION_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                positions = list(reader)
        
        positions.append({
            'symbol': data.get('symbol', ''),
            'name': data.get('name', ''),
            'quantity': str(data.get('quantity', 0)),
            'cost_price': str(data.get('cost_price', 0))
        })
        
        with open(POSITION_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['symbol', 'name', 'quantity', 'cost_price'])
            writer.writeheader()
            writer.writerows(positions)
        
        return jsonify({"success": True})
    
    if request.method == 'DELETE':
        symbol = request.args.get('symbol', '')
        if os.path.exists(POSITION_FILE):
            positions = []
            with open(POSITION_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                positions = [p for p in reader if p['symbol'] != symbol]
            
            with open(POSITION_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['symbol', 'name', 'quantity', 'cost_price'])
                writer.writeheader()
                writer.writerows(positions)
        
        return jsonify({"success": True})

@app.route('/api/plan/market-status', methods=['GET'])
def market_status():
    return jsonify({
        "status": "bull",
        "status_text": "牛市",
        "position_suggestion": "80%"
    })

@app.route('/api/plan/adjustment', methods=['GET'])
def adjustment_strategy():
    return jsonify({
        "adjustments": [],
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/plan/buy', methods=['GET'])
def buy_strategy():
    return jsonify({"suggestions": []})

@app.route('/api/backtest', methods=['GET'])
def backtest():
    return jsonify({
        "equity_curve": [],
        "metrics": {
            "total_return": 0,
            "max_drawdown": 0,
            "sharpe_ratio": 0
        }
    })

@app.route('/api/market/overview', methods=['GET'])
def market_overview():
    return jsonify({
        "hs300": {"index": 4000, "change": 0},
        "news": []
    })

@app.route('/api/news', methods=['GET'])
def news():
    return jsonify({"news": []})

@app.route('/api/scheduler/status', methods=['GET'])
def scheduler_status():
    return jsonify({"enabled": False})

@app.route('/api/scheduler/toggle', methods=['POST'])
def scheduler_toggle():
    return jsonify({"success": True, "enabled": False})

@app.route('/api/pdf/generate', methods=['POST'])
def generate_pdf():
    return jsonify({"error": "PDF not available in Vercel"})

def handler(request):
    return app.full_dispatch_request(request)
