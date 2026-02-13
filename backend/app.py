from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import csv
import os
import sys
import time
import random
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os
    
    REPORTLAB_AVAILABLE = True
    
    # 注册中文字体
    def register_chinese_fonts():
        try:
            font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
            if not os.path.exists(font_dir):
                os.makedirs(font_dir)
            
            # 尝试使用系统字体
            system_fonts = [
                ('C:/Windows/Fonts/msyh.ttc', 'msyh', 'Microsoft YaHei'),
                ('C:/Windows/Fonts/simhei.ttf', 'simhei', 'SimHei'),
                ('C:/Windows/Fonts/simsun.ttc', 'simsun', 'SimSun'),
            ]
            
            font_registered = False
            for font_path, font_name, display_name in system_fonts:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        print(f"成功注册字体: {display_name} ({font_name})")
                        font_registered = True
                        break
                    except Exception as e:
                        print(f"注册字体失败 {display_name}: {e}")
                        continue
            
            if not font_registered:
                print("警告: 未找到可用的中文字体，PDF中文显示可能有问题")
                return None
            
            return font_name
        except Exception as e:
            print(f"注册中文字体失败: {e}")
            return None
    
    CHINESE_FONT = register_chinese_fonts()
    
except ImportError:
    REPORTLAB_AVAILABLE = False
    CHINESE_FONT = None
    print("警告: reportlab未安装，PDF导出功能不可用")

# 导入DataProvider类和BacktestEngine类
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from strategy.data_provider import DataProvider
from strategy.backtest_engine import BacktestEngine
from strategy.stock_pool_manager import StockPoolManager
from pdf_scheduler import PDFScheduler
from email_sender import EmailSender
from email_config_manager import EmailConfigManager

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

app = Flask(__name__, static_folder='../web', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})

app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(logging.StreamHandler(sys.stdout))

LOG_DIR = "../logs"
CACHE = {}
CACHE_EXPIRY = 300
CACHE_ACCESS_COUNT = {}

# 初始化PDF调度器
pdf_scheduler = PDFScheduler()

# 初始化邮件发送器
email_config_manager = EmailConfigManager()
email_sender = EmailSender(email_config_manager)

# 模拟数据
class MockStockPoolManager:
    def __init__(self, log_dir=None):
        # 默认股票池，只能通过股票池管理API修改
        self.default_pool = ['600519', '000858', '002371']
        
        # 尝试从文件加载股票池数据
        self.pool_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'strategy', 'data', 'stock_pool.json')
        self.current_pool = self._load_pool()
        
        self.hs300_components = ['600519', '000858']
    
    def _load_pool(self):
        """从文件加载股票池数据"""
        try:
            if os.path.exists(self.pool_file):
                with open(self.pool_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data and isinstance(data, list):
                        print(f"从文件加载股票池: {data}")
                        return data
        except Exception as e:
            print(f"加载股票池文件失败: {e}")
        
        # 如果加载失败，使用默认股票池
        print(f"使用默认股票池: {self.default_pool}")
        return self.default_pool.copy()
    
    def _save_pool(self):
        """将股票池数据保存到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.pool_file), exist_ok=True)
            
            with open(self.pool_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_pool, f, ensure_ascii=False, indent=2)
            print(f"股票池已保存到文件: {self.current_pool}")
        except Exception as e:
            print(f"保存股票池文件失败: {e}")
    
    def get_stock_pool_info(self):
        return {
            'current_pool': self.current_pool,
            'default_pool': self.default_pool,
            'pool_size': len(self.current_pool),
            'hs300_components': self.hs300_components,
            'hs300_size': len(self.hs300_components),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def set_custom_pool(self, stocks):
        # 只有通过股票池管理API调用此方法时才能修改股票池
        self.current_pool = stocks
        self._save_pool()
    
    def add_custom_stock(self, stock):
        # 只有通过股票池管理API调用此方法时才能添加股票
        if stock not in self.current_pool:
            self.current_pool.append(stock)
            self._save_pool()
            return True
        return False
    
    def remove_custom_stock(self, stock):
        # 只有通过股票池管理API调用此方法时才能移除股票
        if stock in self.current_pool:
            self.current_pool.remove(stock)
            self._save_pool()
            return True
        return False
    
    def update_hs300_components(self):
        return self.hs300_components

class MockBacktestEngine:
    def __init__(self, initial_cash=100000):
        pass

class MockMultiStockPredictor:
    def __init__(self, model_type='random_forest'):
        pass

stock_pool_manager = StockPoolManager(log_dir=LOG_DIR)
print(f"StockPoolManager initialized with pool size: {len(stock_pool_manager.current_pool)}")
print(f"StockPoolManager current_pool: {stock_pool_manager.current_pool}")
backtest_engine = BacktestEngine(initial_cash=100000)
multi_predictor = MockMultiStockPredictor(model_type='random_forest')

def get_cached_data(key):
    if key in CACHE:
        data, timestamp = CACHE[key]
        access_count = CACHE_ACCESS_COUNT.get(key, 0)
        
        if access_count == 0:
            expiry = 0.01
        else:
            expiry = CACHE_EXPIRY
        
        if time.time() - timestamp < expiry:
            print(f"返回缓存数据: {key}, 缓存时间: {timestamp}, 访问次数: {access_count}")
            CACHE_ACCESS_COUNT[key] = access_count + 1
            return data
    print(f"缓存未命中: {key}")
    return None

def set_cached_data(key, data):
    CACHE[key] = (data, time.time())
    CACHE_ACCESS_COUNT[key] = 0

def get_mock_stock_data(symbol):
    base_price = 10 + (hash(symbol) % 100)
    change = (hash(symbol + str(time.time())) % 20 - 10) / 10
    open_price = base_price + (hash(symbol + "open") % 10 - 5) / 10
    
    return {
        "symbol": symbol,
        "name": f"股票{symbol}",
        "price": round(base_price + change, 2),
        "open": round(open_price, 2),
        "change": round(change, 2),
        "change_percent": round((change / base_price) * 100, 2),
        "volume": 1000000 + (hash(symbol) % 10000000),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_mock": True
    }

@app.route('/api/login', methods=['POST'])
def login():
    print("API called: /api/login")
    
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        print(f"登录请求: username={username}")
        
        if username == 'admin' and password == 'libo0519':
            print("登录成功")
            return jsonify({
                'success': True,
                'message': '登录成功',
                'username': username
            })
        else:
            print("登录失败: 用户名或密码错误")
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
            
    except Exception as e:
        print(f"登录异常: {e}")
        return jsonify({
            'success': False,
            'message': '登录失败，请稍后重试'
        }), 500

@app.route('/api/stocks/attention', methods=['GET'])
def get_attention_stocks():
    print(f"API called: /api/stocks/attention")
    
    cache_key = 'attention_stocks'
    cached_data = get_cached_data(cache_key)
    if cached_data:
        print(f"Returning cached data for {len(cached_data)} stocks")
        return jsonify({'stocks': cached_data, 'from_cache': True})
    
    stocks_param = request.args.get('stocks')
    if stocks_param:
        stock_list = stocks_param.split(',')
    else:
        stock_list = stock_pool_manager.current_pool
    
    print(f"Stock list: {stock_list}")
    
    result = []
    for symbol in stock_list:
        try:
            print(f"Fetching data for {symbol}...")
            # 使用模拟数据
            result.append(get_mock_stock_data(symbol))
        except Exception as e:
            print(f"获取股票 {symbol} 数据失败: {e}")
            result.append(get_mock_stock_data(symbol))
    
    print(f"Final result: {len(result)} stocks, mock count: {sum(1 for s in result if s.get('is_mock', False))}")
    set_cached_data(cache_key, result)
    
    return jsonify({'stocks': result, 'from_cache': False})

@app.route('/api/stockpool/info', methods=['GET'])
def get_stock_pool_info():
    info = stock_pool_manager.get_stock_pool_info()
    return jsonify(info)

@app.route('/api/stockpool/update', methods=['POST'])
def update_stock_pool():
    data = request.get_json()
    custom_stocks = data.get('stocks')
    adjust = data.get('adjust', False)  # 默认不进行调整，特别是对于导入操作
    
    if custom_stocks:
        stock_pool_manager.set_custom_pool(custom_stocks)
    
    if adjust:
        adjusted_pool, removed = stock_pool_manager.adjust_stock_pool()
        
        if removed:
            new_stocks = stock_pool_manager.select_new_stocks(num_stocks=len(removed), exclude_stocks=adjusted_pool)
            adjusted_pool.extend(new_stocks)
            stock_pool_manager.set_custom_pool(adjusted_pool)
        
        return jsonify({
            'current_pool': adjusted_pool,
            'removed': removed,
            'added': new_stocks if removed else [],
            'message': '股票池更新成功'
        })
    else:
        # 不进行调整，直接返回当前股票池
        return jsonify({
            'current_pool': stock_pool_manager.current_pool,
            'removed': [],
            'added': [],
            'message': '股票池更新成功（跳过调整）'
        })

@app.route('/api/stockpool/add', methods=['POST'])
def add_stock_to_pool():
    data = request.get_json()
    stock_code = data.get('stock_code')
    
    if not stock_code:
        return jsonify({'error': '请提供股票代码'}), 400
    
    success = stock_pool_manager.add_custom_stock(stock_code)
    
    if success:
        return jsonify({'message': f'股票 {stock_code} 添加成功', 'current_pool': stock_pool_manager.current_pool})
    else:
        return jsonify({'error': f'股票 {stock_code} 已在股票池中'}), 400

@app.route('/api/stockpool/remove', methods=['POST'])
def remove_stock_from_pool():
    data = request.get_json()
    stock_code = data.get('stock_code')
    
    if not stock_code:
        return jsonify({'error': '请提供股票代码'}), 400
    
    success = stock_pool_manager.remove_custom_stock(stock_code)
    
    if success:
        return jsonify({'message': f'股票 {stock_code} 移除成功', 'current_pool': stock_pool_manager.current_pool})
    else:
        return jsonify({'error': f'股票 {stock_code} 不在股票池中'}), 400

@app.route('/api/stockpool/clear', methods=['POST'])
def clear_stock_pool():
    stock_pool_manager.set_custom_pool([])
    return jsonify({'message': '股票池已清空', 'current_pool': stock_pool_manager.current_pool})

@app.route('/api/hs300/components', methods=['GET'])
def get_hs300_components():
    components = stock_pool_manager.hs300_components
    
    if not components:
        components = stock_pool_manager.update_hs300_components()
    
    return jsonify({
        'components': components,
        'count': len(components),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/hs300/update', methods=['POST'])
def update_hs300_components():
    components = stock_pool_manager.update_hs300_components()
    
    return jsonify({
        'components': components,
        'count': len(components),
        'message': '沪深300成分股更新成功'
    })

@app.route('/api/backtest/single', methods=['GET'])
def run_single_backtest():
    symbol = request.args.get('symbol', '600519')
    start_date = request.args.get('start_date', '20230101')
    end_date = request.args.get('end_date', datetime.now().strftime('%Y%m%d'))
    fast_period = int(request.args.get('fast_period', 5))
    slow_period = int(request.args.get('slow_period', 20))
    
    print(f"单股回测请求: symbol={symbol}, start_date={start_date}, end_date={end_date}, fast_period={fast_period}, slow_period={slow_period}")
    
    cache_key = f'backtest_{symbol}_{start_date}_{end_date}_{fast_period}_{slow_period}'
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return jsonify({'result': cached_data, 'from_cache': True})
    
    try:
        # 模拟回测结果
        result = {
            'symbol': symbol,
            'start_date': start_date,
            'end_date': end_date,
            'total_return': round(random.uniform(-0.2, 0.5), 4),
            'max_drawdown': round(random.uniform(0.1, 0.3), 4),
            'sharpe_ratio': round(random.uniform(0.5, 2.0), 4),
            'trades': 25,
            'win_rate': round(random.uniform(0.4, 0.7), 4),
            'profit_factor': round(random.uniform(1.0, 2.5), 4)
        }
        print(f"回测结果: {result}")
        
        set_cached_data(cache_key, result)
        return jsonify({'result': result, 'from_cache': False})
    except Exception as e:
        print(f"回测异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'回测失败: {str(e)}'}), 500

@app.route('/api/backtest/multi', methods=['POST'])
def run_multi_backtest():
    data = request.get_json()
    symbols = data.get('symbols', stock_pool_manager.current_pool)
    start_date = data.get('start_date', '20230101')
    end_date = data.get('end_date', datetime.now().strftime('%Y%m%d'))
    fast_period = data.get('fast_period', 5)
    slow_period = data.get('slow_period', 20)
    initial_cash = int(data.get('initial_cash', 1000000))
    transaction_cost = float(data.get('transaction_cost', 0.3)) / 1000  # 转换为‰为小数
    strategy_type = data.get('strategy_type', 'moving_average')
    
    print(f"多股回测请求: symbols={symbols}, start_date={start_date}, end_date={end_date}")
    print(f"回测参数: initial_cash={initial_cash}, transaction_cost={transaction_cost}, strategy_type={strategy_type}")
    
    cache_key = f'multi_backtest_{"_".join(symbols)}_{start_date}_{end_date}_{fast_period}_{slow_period}_{initial_cash}_{transaction_cost}_{strategy_type}'
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return jsonify({'result': cached_data, 'from_cache': True})
    
    try:
        print(f"开始执行多股回测，策略类型: {strategy_type}")
        print(f"股票列表: {symbols}")
        print(f"日期范围: {start_date} 到 {end_date}")
        
        result = backtest_engine.run_multi_stock_backtest(
            symbols=symbols, 
            start_date=start_date, 
            end_date=end_date, 
            fast_period=fast_period, 
            slow_period=slow_period,
            initial_cash=initial_cash,
            transaction_cost=transaction_cost,
            strategy_type=strategy_type
        )
        
        print(f"回测完成，结果类型: {type(result)}")
        
        if result:
            print(f"回测成功，股票数量: {len(result.get('individual_results', []))}")
            set_cached_data(cache_key, result)
            return jsonify({'result': result, 'from_cache': False})
        else:
            print("回测失败: 没有返回结果")
            return jsonify({'error': '回测失败，请检查股票代码和日期范围'}), 400
    except Exception as e:
        print(f"回测异常: {e}")
        import traceback
        error_trace = traceback.format_exc()
        print(f"异常堆栈: {error_trace}")
        return jsonify({'error': f'回测失败: {str(e)}', 'traceback': error_trace}), 500

@app.route('/api/predict/single', methods=['GET'])
def predict_single_stock():
    symbol = request.args.get('symbol', '600519')
    start_date = request.args.get('start_date', '20230101')
    predict_days = int(request.args.get('days', 5))
    
    try:
        df = DataProvider.get_kline_data(symbol, start_date, datetime.now().strftime('%Y%m%d'))
        
        if df is None or df.empty:
            return jsonify({'error': '获取股票数据失败'}), 400
        
        # 确保只包含数值列
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        if numeric_df.empty or not all(col in numeric_df.columns for col in ['open', 'close', 'high', 'low', 'volume']):
            return jsonify({'error': '获取股票数据失败'}), 400
        
        # 使用简单的预测逻辑
        last_price = numeric_df['close'].iloc[-1]
        predictions = []
        for i in range(predict_days):
            predictions.append({
                'day': i + 1,
                'predicted_price': round(last_price * (1 + (i+1)*0.001), 2)
            })
        
        result = {
            'symbol': symbol,
            'train_result': {
                'mae': 0.0,
                'rmse': 0.0,
                'mape': 0.0,
                'accuracy': 0.0,
                'train_samples': 0,
                'test_samples': 0
            },
            'predict_result': {
                'last_price': round(last_price, 2),
                'direction': 'up',
                'change_percent': 0.0,
                'predictions': predictions
            }
        }
        
        return jsonify({'result': result})
    except Exception as e:
        import traceback
        error_info = {
            'error': f'预测失败: {str(e)}',
            'traceback': traceback.format_exc()
        }
        return jsonify(error_info), 500

@app.route('/api/predict/batch', methods=['POST'])
def predict_batch_stocks():
    data = request.get_json()
    symbols = data.get('symbols', stock_pool_manager.current_pool)
    start_date = data.get('start_date', '20230101')
    predict_days = data.get('days', 5)
    model_type = data.get('model_type', 'random_forest')
    
    print(f"收到批量预测请求: symbols={symbols}, start_date={start_date}, predict_days={predict_days}")
    
    try:
        # 过滤掉非数字的股票代码
        valid_symbols = [s for s in symbols if s.isdigit() and len(s) == 6]
        print(f"过滤后的有效股票代码: {valid_symbols}")
        
        if not valid_symbols:
            return jsonify({'error': '没有有效的股票代码'}), 400
        
        stock_data_dict = {}
        for symbol in valid_symbols:
            print(f"处理股票: {symbol}")
            try:
                df = DataProvider.get_kline_data(symbol, start_date, datetime.now().strftime('%Y%m%d'))
                print(f"获取数据结果: df={df}")
                
                if df is not None and not df.empty:
                    print(f"数据框列: {df.columns.tolist()}")
                    print(f"数据框类型: {df.dtypes}")
                    
                    # 确保只包含数值列
                    numeric_df = df.select_dtypes(include=['int64', 'float64'])
                    print(f"数值列: {numeric_df.columns.tolist()}")
                    
                    if not numeric_df.empty and all(col in numeric_df.columns for col in ['open', 'close', 'high', 'low', 'volume']):
                        # 进一步确保close列是数值类型
                        if pd.api.types.is_numeric_dtype(numeric_df['close']):
                            stock_data_dict[symbol] = numeric_df
                            print(f"添加股票 {symbol} 到数据字典")
            except Exception as e:
                print(f"获取股票 {symbol} 数据时出错: {e}")
                continue
        
        print(f"构建的数据字典键: {list(stock_data_dict.keys())}")
        
        if not stock_data_dict:
            return jsonify({'error': '获取股票数据失败'}), 400
        
        # 使用StockPredictor进行预测
        predictor = StockPredictor(model_type=model_type)
        results = []
        
        for symbol, df in stock_data_dict.items():
            try:
                print(f"预测股票: {symbol}, 模型类型: {model_type}")
                
                # 获取实时价格
                current_price = DataProvider.get_current_price(symbol)
                if current_price:
                    print(f"获取到实时价格: {current_price}")
                else:
                    print(f"无法获取实时价格，使用历史数据的最后收盘价")
                
                train_result = predictor.train(df)
                
                if 'error' in train_result:
                    print(f"训练失败: {train_result['error']}")
                    continue
                
                predict_result = predictor.predict(df, days=predict_days, current_price=current_price)
                
                if 'error' in predict_result:
                    print(f"预测失败: {predict_result['error']}")
                    continue
                
                results.append({
                    'symbol': symbol,
                    'train_result': train_result,
                    'predict_result': predict_result
                })
                print(f"完成股票 {symbol} 的预测")
            except Exception as e:
                print(f'处理股票 {symbol} 时出错: {e}')
                import traceback
                traceback.print_exc()
                continue
        
        print(f"预测结果数量: {len(results)}")
        
        if not results:
            return jsonify({'error': '预测失败，请检查股票数据'}), 400
        
        return jsonify({'results': results})
    except Exception as e:
        import traceback
        print(f"批量预测失败: {e}")
        traceback.print_exc()
        error_info = {
            'error': f'批量预测失败: {str(e)}',
            'traceback': traceback.format_exc()
        }
        return jsonify(error_info), 500

@app.route('/api/stocks/kline', methods=['GET'])
def get_stock_kline():
    symbol = request.args.get('symbol', '000001')
    start_date = request.args.get('start_date', '20230101')
    
    cache_key = f'kline_{symbol}_{start_date}'
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return jsonify({'kline': cached_data, 'from_cache': True})
    
    try:
        df = DataProvider.get_kline_data(symbol, start_date, datetime.now().strftime('%Y%m%d'))
        
        if df is None or df.empty:
            return jsonify({'error': '获取K线数据失败'}), 400
        
        kline_list = []
        for idx, row in df.iterrows():
            kline_list.append({
                "date": idx.strftime('%Y-%m-%d'),
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": int(row['volume'])
            })
        
        set_cached_data(cache_key, kline_list)
        
        return jsonify({'kline': kline_list, 'from_cache': False})
    except Exception as e:
        return jsonify({'error': f'获取K线数据失败: {str(e)}'}), 500

@app.route('/api/strategy/status', methods=['GET'])
def get_strategy_status():
    return jsonify({
        "status": "running",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_stocks": stock_pool_manager.current_pool,
        "stock_pool_size": len(stock_pool_manager.current_pool),
        "hs300_size": len(stock_pool_manager.hs300_components),
        "strategy_params": {
            "fast_period": 5,
            "slow_period": 20,
            "position_pct": 20.0
        }
    })

@app.route('/api/strategy/params', methods=['GET'])
def get_strategy_params():
    return jsonify({
        "peThreshold": 30,
        "roeThreshold": 10,
        "smaShort": 5,
        "smaLong": 20,
        "position_pct": 20.0
    })

@app.route('/api/data/settings', methods=['GET'])
def get_data_settings():
    return jsonify({
        "dataSource": "efinance",
        "cacheExpiry": 3600,
        "enableCache": True,
        "updateFrequency": 30,
        "update_interval": pdf_scheduler.data_update_interval
    })

@app.route('/api/data/settings', methods=['POST'])
def save_data_settings():
    data = request.get_json()
    print('保存数据设置:', data)
    
    # 检查是否是数据更新配置
    if 'update_interval' in data:
        update_interval = data.get('update_interval')
        
        if update_interval is None:
            return jsonify({'error': 'update_interval参数不能为空'}), 400
        
        if not isinstance(update_interval, int):
            return jsonify({'error': 'update_interval必须是整数'}), 400
        
        if update_interval < 1 or update_interval > 120:
            return jsonify({'error': 'update_interval必须在1-120分钟之间'}), 400
        
        pdf_scheduler.set_data_update_interval(update_interval)
        
        return jsonify({
            'message': '数据更新配置已更新',
            'update_interval': update_interval
        })
    
    return jsonify({"message": "数据设置保存成功"})

@app.route('/api/plan/position/init', methods=['POST'])
def init_position_table():
    """初始化持仓表"""
    print("API called: /api/plan/position/init")
    
    try:
        position_file = get_position_file_path()
        
        # 创建默认持仓数据
        default_positions = [
            {
                "symbol": "600519",
                "name": "贵州茅台",
                "quantity": 100,
                "cost_price": 1800.00,
                "current_price": 2023.00,
                "profit_loss": 22300.00,
                "profit_loss_percent": 12.39
            },
            {
                "symbol": "000858",
                "name": "五粮液",
                "quantity": 200,
                "cost_price": 150.00,
                "current_price": 165.00,
                "profit_loss": 3000.00,
                "profit_loss_percent": 10.00
            },
            {
                "symbol": "002371",
                "name": "北方华创",
                "quantity": 500,
                "cost_price": 18.00,
                "current_price": 19.50,
                "profit_loss": 750.00,
                "profit_loss_percent": 8.33
            }
        ]
        
        # 保存默认数据到文件
        with open(position_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['symbol', 'name', 'quantity', 'cost_price', 'current_price', 'profit_loss', 'profit_loss_percent']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(default_positions)
        
        # 清除缓存
        cache_key = 'position_analysis'
        if cache_key in CACHE:
            del CACHE[cache_key]
        
        print(f"持仓表初始化成功: {position_file}")
        return jsonify({"message": "持仓表初始化成功", "positions": default_positions})
    except Exception as e:
        print(f"持仓表初始化失败: {e}")
        return jsonify({"error": f"持仓表初始化失败: {str(e)}"}), 500

@app.route('/api/general/settings', methods=['GET'])
def get_general_settings():
    return jsonify({
        "systemLanguage": "zh-CN",
        "timezone": "Asia/Shanghai",
        "theme": "light",
        "autoUpdate": True,
        "enableNotification": True,
        "defaultStrategy": "niu_huicai"
    })

@app.route('/api/general/settings', methods=['POST'])
def save_general_settings():
    data = request.get_json()
    print('保存通用设置:', data)
    # 这里可以添加保存通用设置到配置文件的逻辑
    return jsonify({"message": "通用设置保存成功", "defaultStrategy": data.get('defaultStrategy', 'niu_huicai')})

@app.route('/api/plan/market-status', methods=['GET'])
def get_market_status():
    print("API called: /api/plan/market-status")
    
    cache_key = 'market_status'
    
    import pandas as pd
    import os
    from datetime import datetime
    
    try:
        # 首先尝试从 baostock 获取沪深300指数数据
        print("尝试从 baostock 获取沪深300指数数据")
        try:
            import baostock as bs
            lg = bs.login()
            if lg.error_code == '0':
                # 获取最近120天的沪深300数据
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - pd.Timedelta(days=150)).strftime("%Y-%m-%d")
                
                rs = bs.query_history_k_data_plus(
                    "sh.000300",
                    "date,open,high,low,close,volume",
                    start_date=start_date,
                    end_date=end_date,
                    frequency="d",
                    adjustflag="3"
                )
                
                if rs.error_code == '0':
                    data_list = []
                    while (rs.error_code == '0') & rs.next():
                        data_list.append(rs.get_row_data())
                    
                    if data_list:
                        df = pd.DataFrame(data_list, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                        df["datetime"] = pd.to_datetime(df["datetime"])
                        df.set_index("datetime", inplace=True)
                        
                        # 确保数值列是数值类型
                        numeric_cols = ['open', 'close', 'high', 'low', 'volume']
                        for col in numeric_cols:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                        print(f"baostock成功获取沪深300指数数据 ({len(df)} 条记录)")
                        bs.logout()
                        
                        # 按日期排序
                        df.sort_index(inplace=True)
                        
                        # 获取最新数据
                        latest_data = df.iloc[-1]
                        hs300_index = round(latest_data['close'], 2)
                        
                        # 计算120日均线（如果数据不足120天，使用可用数据计算）
                        if len(df) >= 120:
                            df['ma120'] = df['close'].rolling(window=120).mean()
                            ma120 = round(df.iloc[-1]['ma120'], 2)
                        else:
                            # 数据不足120天，使用60日均线
                            df['ma120'] = df['close'].rolling(window=min(60, len(df))).mean()
                            ma120 = round(df.iloc[-1]['ma120'], 2)
                        
                        # 计算涨跌幅
                        if len(df) >= 2:
                            previous_close = df.iloc[-2]['close']
                            hs300_change = round(((hs300_index - previous_close) / previous_close) * 100, 2)
                        else:
                            hs300_change = 0.0
                        
                        # 生成图表数据（最近7天）
                        if len(df) >= 7:
                            recent_df = df.tail(7)
                            labels = [date.strftime('%m-%d') for date in recent_df.index]
                            hs300_values = [round(val, 2) for val in recent_df['close'].values]
                            ma120_values = [round(val, 2) for val in recent_df['ma120'].values]
                        else:
                            labels = ["01-20", "01-21", "01-22", "01-23", "01-24", "01-25", "01-26"]
                            hs300_values = [3750, 3780, 3760, 3800, 3820, 3810, hs300_index]
                            ma120_values = [3700, 3710, 3720, 3730, 3740, 3750, ma120]
                        
                        chart_data = {
                            "labels": labels,
                            "hs300": hs300_values,
                            "ma120": ma120_values
                        }
                        
                        # 判断市场状态
                        is_bull = hs300_index > ma120
                        
                        result = {
                            "status": "bull" if is_bull else "bear",
                            "status_text": "牛市" if is_bull else "熊市",
                            "position_suggestion": "80%" if is_bull else "30%",
                            "hs300_index": hs300_index,
                            "hs300_change": hs300_change,
                            "ma120": ma120,
                            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "chart_data": chart_data
                        }
                        
                        set_cached_data(cache_key, result)
                        print(f"返回市场状态: {result['status_text']}, 沪深300指数: {hs300_index}")
                        return jsonify(result)
                
                bs.logout()
        except Exception as e:
            print(f"从 baostock 获取沪深300数据失败: {e}")
        
        # 从本地沪深300历史数据库读取数据
        print("从本地沪深300历史数据库读取数据")
        
        # 数据文件路径
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strategy', 'data')
        file_path = os.path.join(data_dir, 'hs300_data.csv')
        
        if os.path.exists(file_path):
            # 读取CSV文件
            df = pd.read_csv(file_path, index_col='datetime', parse_dates=True)
            print(f"成功从本地文件加载沪深300指数数据 ({len(df)} 条记录)")
            
            # 按日期排序
            df.sort_index(inplace=True)
            
            # 获取最新数据
            latest_data = df.iloc[-1]
            hs300_index = round(latest_data['close'], 2)
            
            # 计算120日均线
            if 'ma120' in df.columns:
                ma120 = round(latest_data['ma120'], 2)
            else:
                df['ma120'] = df['close'].rolling(window=120).mean()
                ma120 = round(df.iloc[-1]['ma120'], 2)
            
            # 计算涨跌幅
            if len(df) >= 2:
                previous_close = df.iloc[-2]['close']
                hs300_change = round(((hs300_index - previous_close) / previous_close) * 100, 2)
            else:
                hs300_change = 0.0
            
            # 生成图表数据（最近7天）
            if len(df) >= 7:
                recent_df = df.tail(7)
                labels = [date.strftime('%m-%d') for date in recent_df.index]
                hs300_values = [round(val, 2) for val in recent_df['close'].values]
                ma120_values = [round(val, 2) for val in recent_df['ma120'].values]
            else:
                # 如果数据不足7天，使用默认数据
                labels = ["01-20", "01-21", "01-22", "01-23", "01-24", "01-25", "01-26"]
                hs300_values = [3750, 3780, 3760, 3800, 3820, 3810, hs300_index]
                ma120_values = [3700, 3710, 3720, 3730, 3740, 3750, ma120]
            
            chart_data = {
                "labels": labels,
                "hs300": hs300_values,
                "ma120": ma120_values
            }
            
        else:
            print(f"沪深300指数数据文件不存在: {file_path}")
            # 如果文件不存在，使用模拟数据
            import random
            hs300_index = round(3800 + random.uniform(-50, 50), 2)
            hs300_change = round(random.uniform(-2, 2), 2)
            ma120 = round(3760 + random.uniform(-30, 30), 2)
            
            chart_data = {
                "labels": ["01-20", "01-21", "01-22", "01-23", "01-24", "01-25", "01-26"],
                "hs300": [3750, 3780, 3760, 3800, 3820, 3810, hs300_index],
                "ma120": [3700, 3710, 3720, 3730, 3740, 3750, ma120]
            }
        
    except Exception as e:
        print(f"读取沪深300数据失败: {e}")
        # 出错时使用模拟数据
        import random
        hs300_index = round(3800 + random.uniform(-50, 50), 2)
        hs300_change = round(random.uniform(-2, 2), 2)
        ma120 = round(3760 + random.uniform(-30, 30), 2)
        
        chart_data = {
            "labels": ["01-20", "01-21", "01-22", "01-23", "01-24", "01-25", "01-26"],
            "hs300": [3750, 3780, 3760, 3800, 3820, 3810, hs300_index],
            "ma120": [3700, 3710, 3720, 3730, 3740, 3750, ma120]
        }
    
    # 判断市场状态
    is_bull = hs300_index > ma120
    
    result = {
        "status": "bull" if is_bull else "bear",
        "status_text": "牛市" if is_bull else "熊市",
        "position_suggestion": "80%" if is_bull else "30%",
        "hs300_index": hs300_index,
        "hs300_change": hs300_change,
        "ma120": ma120,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "chart_data": chart_data
    }
    
    set_cached_data(cache_key, result)
    print(f"返回市场状态: {result['status_text']}, 沪深300指数: {hs300_index}")
    return jsonify(result)

def get_position_file_path():
    """获取持仓数据文件路径"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'strategy', 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'position_data.csv')

@app.route('/api/plan/position', methods=['GET'])
def get_position_analysis():
    print("API called: /api/plan/position")
    
    # 打印请求参数
    print(f"请求参数: {request.args}")
    
    # 从本地文件读取持仓数据
    position_file = get_position_file_path()
    positions = []
    
    try:
        if os.path.exists(position_file):
            print(f"从本地文件读取持仓数据: {position_file}")
            with open(position_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                positions = list(reader)
                
            # 转换数据类型（直接使用文件中的价格，不获取实时价格）
            updated_positions = []
            for pos in positions:
                try:
                    symbol = pos['symbol']
                    name = pos['name']
                    quantity = int(pos['quantity'])
                    cost_price = float(pos['cost_price'])
                    
                    # 获取实时股票价格
                    print(f"开始获取 {symbol} ({name}) 的实时价格...")
                    current_price = DataProvider.get_current_price(symbol)
                    print(f"DataProvider.get_current_price({symbol}) 返回: {current_price}")
                    
                    if current_price is not None and current_price > 0:
                        print(f"获取到 {symbol} ({name}) 实时价格: {current_price}")
                    else:
                        # 如果获取失败，使用文件中的价格
                        current_price = float(pos['current_price'])
                        print(f"获取 {symbol} ({name}) 实时价格失败，使用文件中的价格: {current_price}")
                    
                    # 重新计算盈亏和盈亏百分比
                    profit_loss = (current_price - cost_price) * quantity
                    profit_loss_percent = (profit_loss / (cost_price * quantity)) * 100 if cost_price > 0 else 0
                    
                    updated_pos = {
                        'symbol': symbol,
                        'name': name,
                        'quantity': quantity,
                        'cost_price': cost_price,
                        'current_price': current_price,
                        'profit_loss': profit_loss,
                        'profit_loss_percent': profit_loss_percent
                    }
                    updated_positions.append(updated_pos)
                    
                except Exception as e:
                    print(f"处理持仓数据失败: {e}")
                    # 如果处理失败，使用原始数据
                    pos['quantity'] = int(pos['quantity'])
                    pos['cost_price'] = float(pos['cost_price'])
                    pos['current_price'] = float(pos['current_price'])
                    pos['profit_loss'] = float(pos['profit_loss'])
                    pos['profit_loss_percent'] = float(pos['profit_loss_percent'])
                    updated_positions.append(pos)
            
            positions = updated_positions
            
            # 保存更新后的数据回文件
            try:
                with open(position_file, 'w', encoding='utf-8', newline='') as f:
                    fieldnames = ['symbol', 'name', 'quantity', 'cost_price', 'current_price', 'profit_loss', 'profit_loss_percent']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(positions)
                print(f"持仓数据已更新并保存: {position_file}")
            except Exception as e:
                print(f"保存持仓数据失败: {e}")
                # 保存失败不影响返回数据
                
        else:
            print(f"持仓数据文件不存在，创建空文件: {position_file}")
            # 创建空持仓数据
            positions = []
            # 确保目录存在
            os.makedirs(os.path.dirname(position_file), exist_ok=True)
            print(f"目录已确保存在: {os.path.dirname(position_file)}")
            # 保存空数据到文件（只写表头）
            with open(position_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['symbol', 'name', 'quantity', 'cost_price', 'current_price', 'profit_loss', 'profit_loss_percent']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
            print(f"空文件创建成功: {position_file}")
    except Exception as e:
        print(f"读取持仓数据失败: {e}")
        # 使用空数据
        positions = []
    
    # 计算持仓市值
    position_value = 0.0
    total_cost = 0.0
    for pos in positions:
        try:
            # 确保current_price和quantity是数字类型
            current_price = float(pos.get('current_price', 0))
            quantity = int(pos.get('quantity', 0))
            cost_price = float(pos.get('cost_price', 0))
            position_value += current_price * quantity
            total_cost += cost_price * quantity
        except (ValueError, TypeError) as e:
            print(f"计算持仓市值时出错: {e}")
            continue
    
    # 从请求参数获取available_cash
    available_cash = request.args.get('available_cash', None, type=float)
    
    # 如果请求参数中没有提供，则从配置文件中读取
    if available_cash is None:
        try:
            cash_config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'cash_config.json')
            if os.path.exists(cash_config_file):
                with open(cash_config_file, 'r', encoding='utf-8') as f:
                    cash_config = json.load(f)
                    available_cash = cash_config.get('available_cash', 187500.00)
                    print(f"从配置文件读取的可用现金: {available_cash}")
            else:
                available_cash = 187500.00
        except Exception as e:
            print(f"读取可用资金配置失败: {e}")
            available_cash = 187500.00
    
    print(f"最终使用的可用现金: {available_cash}")
    
    # 从请求参数获取original_cash
    original_cash = request.args.get('original_cash', None, type=float)
    print(f"从请求参数获取的原始资金: {original_cash}")
    print(f"原始资金类型: {type(original_cash)}")
    print(f"原始资金是否为None: {original_cash is None}")
    
    # 计算总资产
    total_assets = position_value + available_cash
    print(f"计算的总资产: {total_assets}")
    
    # 计算总盈亏
    if original_cash and original_cash > 0:
        total_profit_loss = total_assets - original_cash
        total_profit_loss_percent = (total_profit_loss / original_cash * 100)
        print(f"使用原始资金计算盈亏: total_assets={total_assets}, original_cash={original_cash}, profit_loss={total_profit_loss}")
    else:
        total_profit_loss = position_value - total_cost
        total_profit_loss_percent = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
        print(f"使用成本计算盈亏: position_value={position_value}, total_cost={total_cost}, profit_loss={total_profit_loss}")
    
    # 计算当前仓位
    current_position = f"{(position_value / total_assets * 100):.1f}%"
    
    result = {
        "total_assets": total_assets,
        "position_value": position_value,
        "total_profit_loss": total_profit_loss,
        "total_profit_loss_percent": total_profit_loss_percent,
        "current_position": current_position,
        "available_cash": available_cash,
        "original_cash": original_cash if original_cash is not None else 0,
        "positions": positions,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    print(f"返回结果: {result}")
    print(f"返回结果中的original_cash: {result.get('original_cash')}")
    
    # 不使用缓存，确保每次都计算最新的结果
    return jsonify(result)

@app.route('/api/plan/position', methods=['POST'])
def create_position():
    """创建新持仓"""
    print("API called: /api/plan/position (POST)")
    
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['symbol', 'quantity', 'cost_price']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必要字段: {field}"}), 400
        
        # 获取股票信息
        symbol = data['symbol']
        
        # 获取市场状态
        market_status_response = get_market_status()
        market_status = market_status_response.get_json()
        is_bull_market = market_status.get('status') == 'bull'
        market_state = '牛' if is_bull_market else '熊'
        print(f"当前市场状态: {market_state}")
        
        # 读取现有持仓数据
        position_file = get_position_file_path()
        positions = []
        
        if os.path.exists(position_file):
            with open(position_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                positions = list(reader)
        
        # 计算总资产
        available_cash = 187500.00
        try:
            cash_config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'cash_config.json')
            if os.path.exists(cash_config_file):
                with open(cash_config_file, 'r', encoding='utf-8') as f:
                    cash_config = json.load(f)
                    available_cash = cash_config.get('available_cash', 187500.00)
        except Exception as e:
            print(f"读取可用资金配置失败: {e}")
        
        # 计算持仓市值
        position_value = 0
        for pos in positions:
            try:
                quantity = int(pos['quantity'])
                current_price = float(pos['current_price'])
                position_value += quantity * current_price
            except Exception as e:
                print(f"计算持仓市值失败: {e}")
        
        total_assets = available_cash + position_value
        print(f"总资产: {total_assets}, 可用资金: {available_cash}, 持仓市值: {position_value}")
        
        # 仓位控制策略：牛市80%，熊市30%
        target_position_pct = 0.8 if is_bull_market else 0.3
        target_position_value = total_assets * target_position_pct
        print(f"目标仓位: {target_position_pct * 100}%, 目标持仓市值: {target_position_value}")
        
        # 检查当前仓位是否已超过目标仓位
        if position_value >= target_position_value:
            return jsonify({"error": f"当前仓位已达到目标仓位{target_position_pct * 100}%，无法继续买入"}), 400
        
        # 计算可用买入金额
        available_buy_amount = min(available_cash, target_position_value - position_value)
        print(f"可用买入金额: {available_buy_amount}")
        
        # 股票代码到名称的映射表
        stock_name_map = {
            '002371': '北方华创',
            '002368': '太极股份',
            '300024': '机器人',
            '600118': '中国卫星',
            '603259': '药明康德',
            '600519': '贵州茅台',
            '000858': '五粮液',
            '000001': '平安银行',
            '601318': '中国平安',
            '600036': '招商银行',
            '600276': '恒瑞医药',
            '601888': '中国中免',
            '600887': '伊利股份',
            '000333': '美的集团',
            '000651': '格力电器',
            '600031': '三一重工',
            '000002': '万科A',
            '601988': '中国银行',
            '601288': '农业银行',
            '601398': '工商银行',
            '600000': '浦发银行',
            '601166': '兴业银行',
            '600016': '民生银行',
            '601818': '光大银行',
            '601628': '中国人寿',
            '601336': '新华保险',
            '601601': '中国太保',
            '600030': '中信证券',
            '601688': '华泰证券',
            '601211': '国泰君安',
            '600837': '海通证券',
            '601901': '方正证券',
            '000568': '泸州老窖',
            '600809': '山西汾酒',
            '000799': '酒鬼酒',
            '300308': '中际旭创',
            '603000': '人民网',
            '300502': '新易盛',
            '300274': '阳光电源',
            '300750': '宁德时代',
            '601899': '紫金矿业',
            '301269': '华大九天',
            '688981': '中芯国际',
            '688599': '天合光能',
            '688396': '华润微',
            '601766': '中国中车',
            '600157': '永泰能源',
            '688256': '寒武纪',
            '300563': '神宇股份',
            '002079': '苏州固锝'
        }
        
        # 获取股票名称
        if symbol in stock_name_map:
            name = stock_name_map[symbol]
            print(f"从映射表获取股票名称: {name}")
        else:
            # 尝试从DataProvider获取股票信息
            stock_info = DataProvider.get_stock_info(symbol)
            if stock_info:
                name = stock_info['name']
                print(f"从DataProvider获取股票名称: {name}")
            else:
                # 如果无法获取股票信息，使用默认名称
                name = f"股票{symbol}"
                print(f"无法获取股票信息，使用默认名称: {name}")
        
        # 获取当前价格
        current_price = DataProvider.get_current_price(symbol)
        
        if current_price is not None and current_price > 0:
            print(f"从DataProvider获取当前价格成功: {current_price}")
        else:
            # 如果无法获取当前价格，使用成本价
            current_price = float(data['cost_price'])
            print(f"无法获取当前价格，使用成本价: {current_price}")
        
        # 单只股票持仓上限控制：不超过总资产的20%
        max_single_stock_value = total_assets * 0.2
        print(f"单只股票最大持仓市值: {max_single_stock_value}")
        
        # 检查是否已存在相同股票
        existing_index = next((i for i, p in enumerate(positions) if p['symbol'] == symbol), -1)
        if existing_index != -1:
            # 如果已存在，计算当前持仓市值
            existing_quantity = int(positions[existing_index]['quantity'])
            existing_value = existing_quantity * current_price
            print(f"股票 {symbol} 已存在，当前持仓市值: {existing_value}")
            
            # 检查是否超过单只股票上限
            if existing_value >= max_single_stock_value:
                return jsonify({"error": f"股票 {symbol} 已达到单只股票持仓上限20%"}), 400
            
            # 计算可继续买入的金额
            available_for_stock = min(available_buy_amount, max_single_stock_value - existing_value)
        else:
            # 如果不存在，计算可买入的金额
            available_for_stock = min(available_buy_amount, max_single_stock_value)
        
        print(f"可用于购买股票 {symbol} 的金额: {available_for_stock}")
        
        # 交易数量规则限制：100股整数倍
        max_quantity = int(available_for_stock / current_price)
        max_quantity = (max_quantity // 100) * 100
        
        # 使用请求中的数量，但不超过计算的最大数量
        requested_quantity = int(data['quantity'])
        quantity = min(requested_quantity, max_quantity)
        
        # 确保数量是100的整数倍
        quantity = (quantity // 100) * 100
        
        if quantity < 100:
            return jsonify({"error": f"可用资金不足，无法买入100股"}), 400
        
        print(f"最终买入数量: {quantity} 股")
        
        cost_price = float(data['cost_price'])
        
        profit_loss = (current_price - cost_price) * quantity
        profit_loss_percent = (profit_loss / (cost_price * quantity)) * 100 if cost_price > 0 else 0
        
        # 构建持仓数据
        position = {
            "symbol": symbol,
            "name": name,
            "quantity": quantity,
            "cost_price": cost_price,
            "current_price": current_price,
            "profit_loss": profit_loss,
            "profit_loss_percent": profit_loss_percent
        }
        
        # 读取现有数据
        position_file = get_position_file_path()
        positions = []
        
        if os.path.exists(position_file):
            with open(position_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                positions = list(reader)
        
        # 检查是否已存在相同股票
        existing_index = next((i for i, p in enumerate(positions) if p['symbol'] == symbol), -1)
        
        if existing_index != -1:
            # 如果已存在，增加持仓数量
            existing_quantity = int(positions[existing_index]['quantity'])
            existing_cost_price = float(positions[existing_index]['cost_price'])
            
            # 计算新的平均成本价
            total_quantity = existing_quantity + quantity
            new_cost_price = (existing_quantity * existing_cost_price + quantity * cost_price) / total_quantity
            
            # 更新持仓数据
            positions[existing_index]['quantity'] = total_quantity
            positions[existing_index]['cost_price'] = round(new_cost_price, 2)
            positions[existing_index]['current_price'] = current_price
            positions[existing_index]['name'] = name
            
            # 重新计算盈亏
            profit_loss = (current_price - new_cost_price) * total_quantity
            profit_loss_percent = (profit_loss / (new_cost_price * total_quantity)) * 100 if new_cost_price > 0 else 0
            
            positions[existing_index]['profit_loss'] = round(profit_loss, 2)
            positions[existing_index]['profit_loss_percent'] = round(profit_loss_percent, 2)
            
            print(f"更新持仓成功: {symbol}, 原持仓: {existing_quantity}, 新增: {quantity}, 总持仓: {total_quantity}")
        else:
            # 如果不存在，添加新持仓
            position = {
                "symbol": symbol,
                "name": name,
                "quantity": quantity,
                "cost_price": cost_price,
                "current_price": current_price,
                "profit_loss": profit_loss,
                "profit_loss_percent": profit_loss_percent
            }
            positions.append(position)
            print(f"创建持仓成功: {symbol}")
        
        # 保存到文件
        fieldnames = ['symbol', 'name', 'quantity', 'cost_price', 'current_price', 'profit_loss', 'profit_loss_percent']
        with open(position_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(positions)
        
        # 清除缓存
        cache_key = 'position_analysis'
        if cache_key in CACHE:
            del CACHE[cache_key]
        
        # 更新可用资金
        buy_amount = current_price * quantity
        new_available_cash = available_cash - buy_amount
        try:
            cash_config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'cash_config.json')
            cash_config = {}
            if os.path.exists(cash_config_file):
                with open(cash_config_file, 'r', encoding='utf-8') as f:
                    cash_config = json.load(f)
            cash_config['available_cash'] = new_available_cash
            with open(cash_config_file, 'w', encoding='utf-8') as f:
                json.dump(cash_config, f, indent=2, ensure_ascii=False)
            print(f"更新可用资金: {new_available_cash}")
        except Exception as e:
            print(f"更新可用资金配置失败: {e}")
        
        return jsonify({"message": "创建持仓成功", "position": position if existing_index == -1 else positions[existing_index]}), 201
    except Exception as e:
        print(f"创建持仓失败: {e}")
        return jsonify({"error": f"创建持仓失败: {str(e)}"}), 500

@app.route('/api/plan/position/<symbol>', methods=['PUT'])
def update_position(symbol):
    """更新现有持仓"""
    print(f"API called: /api/plan/position/{symbol} (PUT)")
    
    try:
        data = request.get_json()
        
        # 读取现有数据
        position_file = get_position_file_path()
        positions = []
        
        if not os.path.exists(position_file):
            return jsonify({"error": "持仓数据文件不存在"}), 404
        
        with open(position_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            positions = list(reader)
        
        # 查找要更新的持仓
        existing_index = next((i for i, p in enumerate(positions) if p['symbol'] == symbol), -1)
        if existing_index == -1:
            return jsonify({"error": f"股票 {symbol} 不存在于持仓中"}), 404
        
        # 获取现有持仓
        existing_position = positions[existing_index]
        
        # 更新字段
        name = data.get('name', existing_position['name'])
        quantity = int(data.get('quantity', existing_position['quantity']))
        cost_price = float(data.get('cost_price', existing_position['cost_price']))
        current_price = float(data.get('current_price', existing_position['current_price']))
        
        # 计算盈亏
        profit_loss = (current_price - cost_price) * quantity
        profit_loss_percent = (profit_loss / (cost_price * quantity)) * 100 if cost_price > 0 else 0
        
        # 构建更新后的持仓数据
        updated_position = {
            "symbol": symbol,
            "name": name,
            "quantity": quantity,
            "cost_price": cost_price,
            "current_price": current_price,
            "profit_loss": profit_loss,
            "profit_loss_percent": profit_loss_percent
        }
        
        # 更新持仓
        positions[existing_index] = updated_position
        
        # 保存到文件
        fieldnames = ['symbol', 'name', 'quantity', 'cost_price', 'current_price', 'profit_loss', 'profit_loss_percent']
        with open(position_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(positions)
        
        # 清除缓存
        cache_key = 'position_analysis'
        if cache_key in CACHE:
            del CACHE[cache_key]
        
        # 清除调仓策略缓存
        adjustment_cache_key = 'adjustment_strategy'
        if adjustment_cache_key in CACHE:
            del CACHE[adjustment_cache_key]
        
        print(f"更新持仓成功: {symbol}")
        return jsonify({"message": "更新持仓成功", "position": updated_position}), 200
    except Exception as e:
        print(f"更新持仓失败: {e}")
        return jsonify({"error": f"更新持仓失败: {str(e)}"}), 500

@app.route('/api/plan/position/<symbol>', methods=['DELETE'])
def delete_position(symbol):
    """删除持仓"""
    print(f"API called: /api/plan/position/{symbol} (DELETE)")
    
    try:
        # 读取现有数据
        position_file = get_position_file_path()
        positions = []
        
        if not os.path.exists(position_file):
            return jsonify({"error": "持仓数据文件不存在"}), 404
        
        with open(position_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            positions = list(reader)
        
        # 查找要删除的持仓
        existing_index = next((i for i, p in enumerate(positions) if p['symbol'] == symbol), -1)
        if existing_index == -1:
            return jsonify({"error": f"股票 {symbol} 不存在于持仓中"}), 404
        
        # 保存被删除的持仓信息
        deleted_position = positions[existing_index]
        
        # 删除持仓
        positions.pop(existing_index)
        
        # 保存到文件
        fieldnames = ['symbol', 'name', 'quantity', 'cost_price', 'current_price', 'profit_loss', 'profit_loss_percent']
        with open(position_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(positions)
        
        # 清除缓存
        cache_key = 'position_analysis'
        if cache_key in CACHE:
            del CACHE[cache_key]
        
        # 清除调仓策略缓存
        adjustment_cache_key = 'adjustment_strategy'
        if adjustment_cache_key in CACHE:
            del CACHE[adjustment_cache_key]
        
        print(f"删除持仓成功: {symbol}")
        return jsonify({"message": "删除持仓成功", "position": deleted_position}), 200
    except Exception as e:
        print(f"删除持仓失败: {e}")
        return jsonify({"error": f"删除持仓失败: {str(e)}"}), 500

@app.route('/api/plan/adjustment', methods=['GET'])
def get_adjustment_strategy():
    print("API called: /api/plan/adjustment")
    
    cache_key = 'adjustment_strategy'
    
    if cache_key in CACHE:
        print(f"清除旧的调仓建议缓存: {cache_key}")
        del CACHE[cache_key]
    
    if cache_key in CACHE_ACCESS_COUNT:
        print(f"清除调仓建议访问计数: {cache_key}")
        del CACHE_ACCESS_COUNT[cache_key]
    
    if cache_key in CACHE:
        print(f"返回缓存数据: {cache_key}")
        return jsonify(CACHE[cache_key][0])
    
    print(f"缓存未命中，重新生成调仓建议: {cache_key}")
    
    # 获取当前股票池
    stock_pool = stock_pool_manager.current_pool
    print(f"当前股票池: {stock_pool}")
    
    # 读取持仓数据
    position_file = get_position_file_path()
    positions = []
    
    try:
        if os.path.exists(position_file):
            print(f"从本地文件读取持仓数据: {position_file}")
            with open(position_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                positions = list(reader)
            
            # 转换数据类型并获取实时价格
            for pos in positions:
                try:
                    symbol = pos['symbol']
                    name = pos['name']
                    quantity = int(pos['quantity'])
                    cost_price = float(pos['cost_price'])
                    
                    # 直接使用文件中的价格
                    current_price = float(pos['current_price'])
                    print(f"[DEBUG] 使用 {symbol} 文件中的价格: {current_price}")
                    
                    # 重新计算盈亏和盈亏百分比
                    profit_loss = (current_price - cost_price) * quantity
                    profit_loss_percent = (profit_loss / (cost_price * quantity)) * 100 if cost_price > 0 else 0
                    
                    pos['quantity'] = quantity
                    pos['cost_price'] = cost_price
                    pos['current_price'] = current_price
                    pos['profit_loss'] = profit_loss
                    pos['profit_loss_percent'] = profit_loss_percent
                except (ValueError, TypeError) as e:
                    print(f"转换持仓数据类型失败: {e}")
        else:
            print(f"持仓数据文件不存在: {position_file}")
            print(f"创建空持仓文件: {position_file}")
            os.makedirs(os.path.dirname(position_file), exist_ok=True)
            with open(position_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['symbol', 'name', 'quantity', 'cost_price', 'current_price', 'profit_loss', 'profit_loss_percent']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
            print(f"空持仓文件创建成功")
    except Exception as e:
        print(f"读取持仓数据失败: {e}")
    
    # 生成调仓建议
    suggestions = []
    
    # 检查市场状态，判断是否牛转熊
    try:
        # 获取沪深300数据和120日均线
        import pandas as pd
        import numpy as np
        
        # 尝试从文件读取数据
        hs300_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'strategy', 'data', 'hs300_data.csv')
        if os.path.exists(hs300_file):
            df = pd.read_csv(hs300_file)
            # 确保数据按日期排序
            df = df.sort_values('date')
            
            # 获取最新的沪深300指数和120日均线
            if len(df) > 0:
                latest_data = df.iloc[-1]
                hs300_index = latest_data['close']
                ma120 = latest_data['ma120']
            else:
                # 文件存在但无数据，使用模拟数据
                import random
                hs300_index = round(3800 + random.uniform(-50, 50), 2)
                ma120 = round(3760 + random.uniform(-30, 30), 2)
        else:
            # 文件不存在，使用模拟数据
            import random
            hs300_index = round(3800 + random.uniform(-50, 50), 2)
            ma120 = round(3760 + random.uniform(-30, 30), 2)
        
        # 判断当前市场状态
        is_current_bull = hs300_index > ma120
        
        # 判断是否牛转熊（这里简化处理，实际应该比较历史状态）
        # 由于没有历史状态记录，我们假设如果当前是熊市，就认为可能是牛转熊
        if not is_current_bull and positions:
            # 当市场转为熊市时，建议卖出所有持仓股票，将仓位降至30%
            for pos in positions:
                symbol = pos.get('symbol')
                name = stock_pool_manager.get_stock_name(symbol)
                suggestions.append({
                    "action": "sell",
                    "action_text": "牛转熊",
                    "symbol": symbol,
                    "name": name,
                    "reason": "市场状态从牛市转为熊市",
                    "detail": "建议卖出部分仓位，将整体仓位降至30%"
                })
    except Exception as e:
        print(f"检测市场状态失败: {e}")
    
    # 分析持仓股票，只生成卖出信号的建议
    for pos in positions:
        symbol = pos.get('symbol')
        name = stock_pool_manager.get_stock_name(symbol)
        profit_loss_percent = pos.get('profit_loss_percent', 0)
        current_price = pos.get('current_price', 0)
        
        # 尝试从baostock获取实时价格
        try:
            import baostock as bs
            lg = bs.login()
            if lg.error_code == '0':
                # 获取实时价格
                rs = bs.query_history_k_data_plus(
                    f"sh.{symbol}" if symbol.startswith('6') else f"sz.{symbol}",
                    "date,code,open,high,low,close",
                    start_date=datetime.now().strftime("%Y-%m-%d"),
                    end_date=datetime.now().strftime("%Y-%m-%d"),
                    frequency="d",
                    adjustflag="3"
                )
                
                if rs.error_code == '0':
                    data_list = []
                    while (rs.error_code == '0') & rs.next():
                        data_list.append(rs.get_row_data())
                    
                    if data_list:
                        current_price = float(data_list[0][4])
                        print(f"[DEBUG] 从baostock获取 {symbol} 实时价格: {current_price}")
                bs.logout()
        except Exception as e:
            print(f"从baostock获取 {symbol} 价格失败: {e}")
            # 使用文件中的价格
            current_price = pos.get('current_price', 0)
        
        try:
            # 应用止盈规则（盈利达到10%）
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
            # 应用止损规则（亏损达到4%）
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
        except (ValueError, TypeError) as e:
            print(f"分析持仓股票失败: {e}")
    
    # 不分析股票池中的其他股票，只针对持仓股票生成卖出建议
    
    # 如果没有建议，不添加默认建议，保持空列表
    # 前端会根据空列表显示"无股票卖出建议"
    
    # 构建结果
    result = {
        "rules": [
            {
                "type": "止盈规则",
                "description": "盈利达到10%时，触发止盈建议"
            },
            {
                "type": "止损规则",
                "description": "亏损达到4%时，触发止损建议，严格执行"
            },
            {
                "type": "牛熊转换规则",
                "description": "牛市转熊市：仓位从80%降至30%"
            },
            {
                "type": "盘中调整",
                "description": "每30分钟检查一次持仓"
            }
        ],
        "suggestions": suggestions,
        "update_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    set_cached_data(cache_key, result)
    return jsonify(result)

@app.route('/api/plan/test', methods=['GET'])
def test_api():
    print("=" * 80)
    print("API called: /api/plan/test")
    print("=" * 80)
    return jsonify({"status": "success", "message": "Test API is working"})

@app.route('/api/plan/buy', methods=['GET'])
def get_buy_strategy():
    import sys
    log_file = open("buy_api_debug.log", "a", encoding="utf-8")
    log_file.write("=" * 80 + "\n")
    log_file.write("API called: /api/plan/buy\n")
    log_file.write("=" * 80 + "\n")
    log_file.flush()
    
    print("=" * 80)
    print("API called: /api/plan/buy")
    print("=" * 80)
    app.logger.debug("API called: /api/plan/buy")
    
    # 从当前股票池获取股票列表（不刷新，只读取）
    stock_pool = stock_pool_manager.current_pool
    log_file.write(f"当前股票池大小: {len(stock_pool)}\n")
    log_file.write(f"当前股票池: {stock_pool}\n")
    log_file.flush()
    
    print(f"当前股票池大小: {len(stock_pool)}")
    print(f"当前股票池: {stock_pool}")
    app.logger.debug(f"当前股票池: {stock_pool}")
    
    # 读取当前持仓的股票列表（用于信息展示，不用于过滤）
    def get_held_stocks():
        """获取当前持仓的股票代码列表"""
        position_file = get_position_file_path()
        held_stocks = []
        try:
            if os.path.exists(position_file):
                with open(position_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for pos in reader:
                        held_stocks.append(pos['symbol'])
        except Exception as e:
            print(f"读取持仓数据失败: {e}")
        return held_stocks
    
    held_stocks = get_held_stocks()
    print(f"当前持仓股票: {held_stocks}")
    
    # 生成买入建议（基于牛回踩策略）
    suggestions = []
    
    # 牛回踩策略的买入条件：
    # 基础条件：股价 > 年线（250日均线） AND 5日均量 > 60日均量
    # 信号条件：成交量 < 5日均量的80% AND 收盘价在20日均线上下1.5%范围内
    
    # 先登录baostock一次
    try:
        import baostock as bs
        lg = bs.login()
        baostock_logged_in = lg.error_code == '0'
        log_file.write(f"baostock登录结果: error_code={lg.error_code}, error_msg={lg.error_msg}\n")
        log_file.flush()
        if not baostock_logged_in:
            print(f"baostock登录失败: {lg.error_msg}")
    except Exception as e:
        print(f"baostock登录异常: {e}")
        log_file.write(f"baostock登录异常: {e}\n")
        log_file.flush()
        baostock_logged_in = False
    
    log_file.write(f"开始分析股票池，共 {len(stock_pool)} 只股票\n")
    log_file.flush()
    
    # 分析默认股票池中的股票
    for symbol in stock_pool:
        name = stock_pool_manager.get_stock_name(symbol)
        log_file.write(f"开始分析股票: {symbol} {name}\n")
        log_file.flush()
        app.logger.debug(f"开始分析股票: {symbol} {name}")
        
        # 从baostock获取真实股票数据
        current_price = 0
        ma20 = 0
        ma250 = 0
        volume = 0
        v_ma5 = 0
        v_ma60 = 0
        
        try:
            if baostock_logged_in:
                app.logger.debug(f"baostock已登录，开始获取 {symbol} {name} 的数据")
                # 获取最近365天的数据（确保有足够数据计算年线）
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                
                rs = bs.query_history_k_data_plus(
                    f"sh.{symbol}" if symbol.startswith('6') else f"sz.{symbol}",
                    "date,code,open,high,low,close,volume",
                    start_date=start_date,
                    end_date=end_date,
                    frequency="d",
                    adjustflag="3"
                )
                
                app.logger.debug(f"baostock查询结果: error_code={rs.error_code}, error_msg={rs.error_msg}")
                
                if rs.error_code == '0':
                    data_list = []
                    while (rs.error_code == '0') & rs.next():
                        data_list.append(rs.get_row_data())
                    
                    app.logger.debug(f"[DEBUG] {symbol} {name} - 获取到 {len(data_list)} 天数据")
                    print(f"[DEBUG] {symbol} {name} - 获取到 {len(data_list)} 天数据")
                    
                    # 降低数据量要求，至少200天即可
                    if len(data_list) >= 200:
                        df = pd.DataFrame(data_list, columns=['date', 'code', 'open', 'high', 'low', 'close', 'volume'])
                        df['close'] = pd.to_numeric(df['close'], errors='coerce')
                        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
                        
                        # 获取最新价格
                        current_price = float(df.iloc[-1]['close'])
                        volume = float(df.iloc[-1]['volume'])
                        
                        # 计算均线
                        ma20 = float(df['close'].tail(20).mean())
                        ma250 = float(df['close'].tail(250).mean()) if len(df) >= 250 else float(df['close'].tail(len(df)).mean())
                        v_ma5 = float(df['volume'].tail(5).mean())
                        v_ma60 = float(df['volume'].tail(60).mean())
                        
                        app.logger.debug(f"[DEBUG] {symbol} {name} - 价格: {current_price}, MA20: {ma20}, MA250: {ma250}, 成交量: {volume}, V_MA5: {v_ma5}, V_MA60: {v_ma60}")
                        print(f"[DEBUG] {symbol} {name} - 价格: {current_price}, MA20: {ma20}, MA250: {ma250}, 成交量: {volume}, V_MA5: {v_ma5}, V_MA60: {v_ma60}")
                    else:
                        app.logger.debug(f"[DEBUG] {symbol} {name} - 数据量不足: {len(data_list)} 天")
                        print(f"[DEBUG] {symbol} {name} - 数据量不足: {len(data_list)} 天")
                else:
                    app.logger.debug(f"[DEBUG] {symbol} {name} - 获取K线数据失败: {rs.error_msg}")
                    print(f"[DEBUG] {symbol} {name} - 获取K线数据失败: {rs.error_msg}")
            else:
                app.logger.debug(f"[DEBUG] {symbol} {name} - baostock未登录，跳过")
                print(f"[DEBUG] {symbol} {name} - baostock未登录，跳过")
        except Exception as e:
            app.logger.error(f"从baostock获取 {symbol} 数据失败: {e}", exc_info=True)
            print(f"从baostock获取 {symbol} 数据失败: {e}")
            continue
        
        # 判断是否符合牛回踩策略的买入条件
        # 基础条件：股价 > 年线 AND 5日均量 > 60日均量
        # 确保所有指标都有有效值
        if current_price <= 0 or ma20 <= 0 or ma250 <= 0 or volume <= 0 or v_ma5 <= 0 or v_ma60 <= 0:
            app.logger.debug(f"[DEBUG] {symbol} {name} - 指标无效，跳过")
            print(f"[DEBUG] {symbol} {name} - 指标无效，跳过")
            continue
        
        base_condition = current_price > ma250 and v_ma5 > v_ma60
        
        # 信号条件：缩量（成交量 < 5日均量的80%）AND 回踩20线（收盘价在20日均线上下1.5%范围内）
        shrink_volume = volume < v_ma5 * 0.8
        backtest_ma20 = abs(current_price / ma20 - 1) < 0.015
        signal_condition = shrink_volume and backtest_ma20
        
        app.logger.debug(f"[DEBUG] {symbol} {name} - 基础条件: {base_condition}, 信号条件: {signal_condition}")
        print(f"[DEBUG] {symbol} {name} - 基础条件: {base_condition}, 信号条件: {signal_condition}")
        
        if base_condition and signal_condition:
            # 计算价格区间和止损位
            price_range = f"{round(current_price * 0.98, 2)}-{round(current_price * 1.02, 2)}"
            stop_loss = round(current_price * 0.96, 2)
            
            suggestions.append({
                "action": "buy",
                "action_text": "买入",
                "symbol": symbol,
                "name": name,
                "current_price": current_price,
                "price_range": price_range,
                "stop_loss": stop_loss,
                "reason": "符合牛回踩策略，股价在年线之上，缩量回踩20日线"
            })
            print(f"[DEBUG] {symbol} {name} - 添加到买入建议")
        # 不再添加"观察"性质的建议
    
    # 登出baostock
    if baostock_logged_in:
        try:
            bs.logout()
        except:
            pass
    
    # 构建结果
    result = {
        "conditions": [
            {
                "type": "市场环境",
                "description": "整体处于牛市或熊市，无重大系统性风险"
            },
            {
                "type": "技术条件",
                "description": "目标股票处于上升趋势，出现健康的技术性回调"
            },
            {
                "type": "风险控制",
                "description": "单只股票仓位限制，买入价格区间控制，止损位预设"
            }
        ],
        "suggestions": suggestions,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(f"[DEBUG] 共生成 {len(suggestions)} 条买入建议")
    log_file.write(f"共生成 {len(suggestions)} 条买入建议\n")
    log_file.write("=" * 80 + "\n")
    log_file.close()
    return jsonify(result)

@app.route('/api/plan/news', methods=['GET'])
def get_news():
    print("API called: /api/plan/news")
    
    cache_key = 'news'
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return jsonify(cached_data)
    
    # 读取当前持仓的股票列表
    def get_held_stocks():
        """获取当前持仓的股票代码列表"""
        position_file = get_position_file_path()
        held_stocks = []
        try:
            if os.path.exists(position_file):
                with open(position_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for pos in reader:
                        held_stocks.append(pos['symbol'])
        except Exception as e:
            print(f"读取持仓数据失败: {e}")
        return held_stocks
    
    # 获取买入建议的股票列表
    def get_buy_suggestion_stocks():
        """获取买入建议中的股票代码列表"""
        buy_suggestion_stocks = []
        try:
            # 从当前股票池获取股票列表
            stock_pool = stock_pool_manager.current_pool
            
            held_stocks = get_held_stocks()
            
            # 分析默认股票池中的股票，生成买入建议
            for symbol in stock_pool:
                # 跳过持仓中已有的股票
                if symbol in held_stocks:
                    continue
                
                name = stock_pool_manager.get_stock_name(symbol)
                
                # 模拟股票数据，判断是否符合牛回踩策略的买入条件
                import random
                current_price = round(100 + random.uniform(-20, 20), 2)
                ma20 = round(95 + random.uniform(-15, 15), 2)
                ma60 = round(90 + random.uniform(-10, 10), 2)
                
                # 判断是否符合牛回踩策略的买入条件
                if current_price > ma20 > ma60:
                    buy_suggestion_stocks.append(symbol)
                    
        except Exception as e:
            print(f"获取买入建议股票列表失败: {e}")
        return buy_suggestion_stocks
    
    held_stocks = get_held_stocks()
    buy_suggestion_stocks = get_buy_suggestion_stocks()
    
    # 合并所有相关股票
    all_related_stocks = set(held_stocks + buy_suggestion_stocks)
    print(f"持仓股票: {held_stocks}")
    print(f"买入建议股票: {buy_suggestion_stocks}")
    print(f"所有相关股票: {all_related_stocks}")
    
    # 从 akshare 获取真实新闻
    all_news = []
    try:
        import akshare as ak
        print("尝试从 akshare 获取新闻...")
        
        # 为每只持仓股票获取新闻
        for symbol in held_stocks:
            try:
                print(f"正在获取 {symbol} 的新闻...")
                df = ak.stock_news_em(symbol=symbol)
                
                if df is not None and not df.empty:
                    print(f"成功获取 {symbol} 的 {len(df)} 条新闻")
                    
                    # 转换为新闻格式
                    for _, row in df.head(3).iterrows():  # 每只股票最多取3条新闻
                        news_item = {
                            "title": row.get('新闻标题', ''),
                            "time": row.get('发布时间', ''),
                            "content": row.get('新闻内容', ''),
                            "source": row.get('文章来源', ''),
                            "related_stocks": [symbol]
                        }
                        all_news.append(news_item)
                else:
                    print(f"{symbol} 没有新闻数据")
            except Exception as e:
                print(f"获取 {symbol} 新闻失败: {e}")
        
        # 按时间排序新闻（最新的在前）
        all_news.sort(key=lambda x: x.get('time', ''), reverse=True)
        
        print(f"从 akshare 获取到 {len(all_news)} 条新闻")
    except Exception as e:
        print(f"从 akshare 获取新闻失败: {e}")
        print("使用模拟新闻数据")
        
        # 如果 akshare 失败，使用模拟新闻数据
        all_news = [
            {
                "title": "北方华创：半导体设备订单大幅增长",
                "time": "2026-01-26 10:30",
                "content": "北方华创（002371）公告显示，公司半导体设备订单大幅增长，预计2026年业绩将显著提升。",
                "source": "新浪财经",
                "related_stocks": ["002371"]
            },
            {
                "title": "贵州茅台：拟提高分红比例",
                "time": "2026-01-26 11:00",
                "content": "贵州茅台（600519）公告称，公司拟提高年度分红比例，以回报广大投资者。",
                "source": "东方财富",
                "related_stocks": ["600519"]
            },
            {
                "title": "五粮液：白酒行业景气度持续提升",
                "time": "2026-01-26 12:15",
                "content": "五粮液（000858）表示，白酒行业景气度持续提升，公司产品销售情况良好。",
                "source": "同花顺",
                "related_stocks": ["000858"]
            },
            {
                "title": "药明康德：海外业务拓展顺利",
                "time": "2026-01-26 13:30",
                "content": "药明康德（603259）公告显示，公司海外业务拓展顺利，新增多个重要客户。",
                "source": "东方财富",
                "related_stocks": ["603259"]
            },
            {
                "title": "中国平安：保险业务稳健增长",
                "time": "2026-01-26 14:00",
                "content": "中国平安（601318）公布最新数据，保险业务保持稳健增长态势。",
                "source": "新浪财经",
                "related_stocks": ["601318"]
            },
            {
                "title": "恒瑞医药：新药研发取得突破",
                "time": "2026-01-26 14:45",
                "content": "恒瑞医药（600276）宣布，公司新药研发取得重大突破，即将进入临床试验阶段。",
                "source": "同花顺",
                "related_stocks": ["600276"]
            }
        ]
    
    print(f"新闻数量: {len(all_news)}")
    
    result = {
        "news": all_news,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    set_cached_data(cache_key, result)
    return jsonify(result)

@app.route('/api/plan/schedule', methods=['GET'])
def get_schedule():
    print("API called: /api/plan/schedule")
    
    cache_key = 'schedule'
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return jsonify(cached_data)
    
    # 计算下次调度时间
    now = datetime.now()
    if now.hour < 15:
        next_schedule = now.replace(hour=15, minute=30, second=0, microsecond=0)
    else:
        next_schedule = (now + timedelta(days=1)).replace(hour=15, minute=30, second=0, microsecond=0)
    
    # 模拟计划调度数据
    result = {
        "schedules": [
            {
                "name": "收盘后分析",
                "time": "15:30",
                "tasks": [
                    "获取当日收盘数据",
                    "更新市场状态判断",
                    "分析当日持仓情况",
                    "生成完整的次日操作计划"
                ],
                "result": {
                    "status": "completed",
                    "last_run": "2026-02-02 15:30",
                    "message": "次日操作计划已生成",
                    "details": {
                        "market_status": "牛市",
                        "position_suggestion": "保持80%仓位",
                        "key_stocks": [
                            {"symbol": "002368", "name": "太极股份", "action": "止损"},
                            {"symbol": "300024", "name": "机器人", "action": "止损"}
                        ]
                    }
                }
            },
            {
                "name": "午间分析",
                "time": "12:00",
                "tasks": [
                    "更新上午市场数据",
                    "调整持仓分析",
                    "更新操作建议（如有需要）",
                    "生成午间调整计划"
                ],
                "result": {
                    "status": "pending",
                    "last_run": "2026-02-02 12:00",
                    "message": "等待下次执行"
                }
            },
            {
                "name": "盘中监控",
                "time": "9:00-15:00",
                "interval": "30分钟",
                "tasks": [
                    "监控市场实时变化",
                    "检查持仓盈亏变化",
                    "如遇重大变动，及时提示",
                    "微调操作计划"
                ],
                "result": {
                    "status": "running",
                    "message": "盘中监控运行中",
                    "last_check": "2026-02-02 15:00"
                }
            }
        ],
        "next_schedule": next_schedule.strftime("%Y-%m-%d %H:%M"),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    set_cached_data(cache_key, result)
    return jsonify(result)

@app.route('/api/plan/export-pdf', methods=['GET'])
def export_plan_pdf():
    print("API called: /api/plan/export-pdf")
    
    if not REPORTLAB_AVAILABLE:
        return jsonify({'error': 'PDF导出功能不可用，请安装reportlab库'}), 500
    
    try:
        # 从请求参数获取available_cash和original_cash（模拟前端的localStorage）
        available_cash = request.args.get('available_cash', 187500.00, type=float)
        original_cash = request.args.get('original_cash', 200000.00, type=float)
        
        # 获取所有需要的数据，并传递参数
        market_status = get_market_status().get_json()
        
        # 模拟get_position_analysis的请求，传递参数
        with app.test_request_context(f'/api/plan/position?available_cash={available_cash}&original_cash={original_cash}'):
            position_analysis = get_position_analysis().get_json()
        
        adjustment_strategy = get_adjustment_strategy().get_json()
        buy_strategy = get_buy_strategy().get_json()
        news_data = get_news().get_json()
        
        # 创建PDF文档
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        story = []
        
        # 设置中文字体
        chinese_font = CHINESE_FONT if CHINESE_FONT else 'Helvetica'
        
        # 添加标题
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName=chinese_font
        )
        story.append(Paragraph("每日操作计划", title_style))
        
        # 添加生成时间
        time_style = ParagraphStyle(
            'CustomTime',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName=chinese_font
        )
        story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}", time_style))
        story.append(Spacer(1, 10))
        
        # 添加分隔线
        line_style = ParagraphStyle(
            'LineStyle',
            parent=styles['Normal'],
            fontSize=1,
            leading=10
        )
        story.append(Paragraph("<hr/>", line_style))
        story.append(Spacer(1, 20))
        
        # 1. 市场状态判断
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#667eea'),
            spaceBefore=15,
            spaceAfter=12,
            fontName=chinese_font
        )
        story.append(Paragraph("一、市场状态判断", section_style))
        
        status_text = market_status.get('status_text', '未知')
        status_color = colors.HexColor('#e74c3c') if market_status.get('status') == 'bull' else colors.HexColor('#27ae60')
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            fontName=chinese_font
        )
        story.append(Paragraph(f"<b>市场状态:</b> <font color='{status_color}'>{status_text}</font>", normal_style))
        story.append(Paragraph(f"<b>沪深300指数:</b> {market_status.get('hs300_index', 0):.2f}", normal_style))
        story.append(Paragraph(f"<b>120日均线:</b> {market_status.get('ma120', 0):.2f}", normal_style))
        story.append(Paragraph(f"<b>仓位建议:</b> {market_status.get('position_suggestion', '')}", normal_style))
        story.append(Spacer(1, 20))
        
        # 2. 持仓分析
        story.append(Paragraph("二、持仓分析", section_style))
        
        # 添加持仓概览信息
        overview_data = [
            ['项目', '金额'],
            ['原始资金', f"¥{position_analysis.get('original_cash', 0):,.2f}"],
            ['总资产', f"¥{position_analysis.get('total_assets', 0):,.2f}"],
            ['总盈亏', f"¥{position_analysis.get('total_profit_loss', 0):,.2f}"],
            ['持仓市值', f"¥{position_analysis.get('position_value', 0):,.2f}"],
            ['当前仓位', position_analysis.get('current_position', '0%')]
        ]
        
        overview_table = Table(overview_data, colWidths=[2.5*inch, 2.5*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 0), (-1, 0), chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, 1), chinese_font),
            ('FONTSIZE', (0, 1), (-1, 1), 11),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(overview_table)
        story.append(Spacer(1, 20))
        
        # 添加持仓明细表格
        positions = position_analysis.get('positions', [])
        if positions:
            position_data = [['股票代码', '股票名称', '持仓数量', '成本价', '当前价', '盈亏', '盈亏率']]
            for pos in positions:
                profit_loss = pos.get('profit_loss', 0)
                profit_loss_percent = pos.get('profit_loss_percent', 0)
                
                profit_loss_color = colors.HexColor('#27ae60') if profit_loss < 0 else colors.HexColor('#e74c3c')
                profit_loss_percent_color = colors.HexColor('#27ae60') if profit_loss_percent < 0 else colors.HexColor('#e74c3c')
                
                profit_loss_style = ParagraphStyle(
                    'ProfitLoss',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=profit_loss_color,
                    alignment=TA_CENTER,
                    fontName=chinese_font
                )
                
                profit_loss_percent_style = ParagraphStyle(
                    'ProfitLossPercent',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=profit_loss_percent_color,
                    alignment=TA_CENTER,
                    fontName=chinese_font
                )
                
                position_data.append([
                    pos.get('symbol', ''),
                    pos.get('name', ''),
                    str(pos.get('quantity', 0)),
                    f"{pos.get('cost_price', 0):.2f}",
                    f"{pos.get('current_price', 0):.2f}",
                    Paragraph(f"{profit_loss:.2f}", profit_loss_style),
                    Paragraph(f"{profit_loss_percent:.2f}%", profit_loss_percent_style)
                ])
            
            table = Table(position_data, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke if i % 2 == 0 else colors.HexColor('#f5f7fa') for i in range(len(position_data) - 1)])
            ]))
            story.append(table)
        else:
            story.append(Paragraph("暂无持仓数据", normal_style))
        
        story.append(Spacer(1, 20))
        
        # 3. 调仓策略
        story.append(Paragraph("三、调仓策略", section_style))
        
        suggestions = adjustment_strategy.get('suggestions', [])
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                action_text = suggestion.get('action_text', '')
                symbol = suggestion.get('symbol', '')
                name = suggestion.get('name', '')
                current_price = suggestion.get('current_price', 0)
                reason = suggestion.get('reason', '')
                
                action_color = colors.HexColor('#e74c3c') if suggestion.get('action') == 'sell' else colors.HexColor('#27ae60')
                story.append(Paragraph(
                    f"{i}. <font color='{action_color}'><b>{action_text}</b></font> - {symbol} {name}",
                    normal_style
                ))
                story.append(Paragraph(f"   当前价格: ¥{current_price:.2f}", normal_style))
                story.append(Paragraph(f"   原因: {reason}", normal_style))
                story.append(Spacer(1, 12))
        else:
            story.append(Paragraph("暂无调仓建议", normal_style))
        
        story.append(Spacer(1, 20))
        
        # 4. 买入策略
        story.append(Paragraph("四、买入策略", section_style))
        
        # 获取当前持仓列表，用于过滤已持仓的股票
        held_symbols = []
        positions = position_analysis.get('positions', [])
        if positions:
            held_symbols = [pos.get('symbol', '') for pos in positions]
        
        # 过滤掉已持仓的股票
        buy_suggestions = buy_strategy.get('suggestions', [])
        filtered_suggestions = [s for s in buy_suggestions if s.get('symbol', '') not in held_symbols]
        
        if filtered_suggestions:
            for i, suggestion in enumerate(filtered_suggestions, 1):
                symbol = suggestion.get('symbol', '')
                name = suggestion.get('name', '')
                price_range = suggestion.get('price_range', '')
                stop_loss = suggestion.get('stop_loss', '')
                reason = suggestion.get('reason', '')
                
                story.append(Paragraph(
                    f"{i}. <b>{symbol} {name}</b>",
                    normal_style
                ))
                story.append(Paragraph(f"   价格区间: {price_range}", normal_style))
                story.append(Paragraph(f"   止损位: {stop_loss}", normal_style))
                story.append(Paragraph(f"   原因: {reason}", normal_style))
                story.append(Spacer(1, 12))
        else:
            story.append(Paragraph("暂无买入建议（已过滤持仓股票）", normal_style))
        
        story.append(Spacer(1, 20))
        
        # 5. 资讯整合
        story.append(Paragraph("五、资讯整合", section_style))
        
        news_list = news_data.get('news', [])
        if news_list:
            for i, news in enumerate(news_list, 1):
                title = news.get('title', '')
                time = news.get('time', '')
                content = news.get('content', '')
                
                # 创建资讯卡片样式
                news_box_style = ParagraphStyle(
                    'NewsBox',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.HexColor('#34495e'),
                    leftIndent=10,
                    spaceAfter=12,
                    fontName=chinese_font
                )
                
                story.append(Paragraph(
                    f"<b>{i}. {title}</b> <font color='#7f8c8d'>({time})</font>",
                    news_box_style
                ))
                story.append(Paragraph(f"   {content}", news_box_style))
        else:
            story.append(Paragraph("暂无资讯数据", normal_style))
        
        # 添加页脚
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#95a5a6'),
            alignment=TA_CENTER,
            fontName=chinese_font
        )
        story.append(Paragraph("本报告由量化交易系统自动生成，仅供参考，不构成投资建议。", footer_style))
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        
        # 返回PDF文件
        filename = f"每日操作计划_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"导出PDF失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'导出PDF失败: {str(e)}'}), 500

@app.route('/api/diagnostic/data-source', methods=['GET'])
def diagnostic_data_source():
    """诊断数据源连接状态"""
    print("API called: /api/diagnostic/data-source")
    
    result = {
        'adata': {'status': 'unknown', 'message': '', 'test_symbol': '002371', 'price': None},
        'akshare': {'status': 'unknown', 'message': '', 'test_symbol': '002371', 'price': None},
        'efinance': {'status': 'unknown', 'message': '', 'test_symbol': '002371', 'price': None}
    }
    
    # 测试 adata（第一选择）
    try:
        import adata
        df = adata.stock.market.get_market()
        if df is not None and not df.empty:
            stock_df = df[df['stock_code'] == '002371']
            if not stock_df.empty:
                price = float(stock_df['close'].values[0])
                result['adata'] = {
                    'status': 'success',
                    'message': f'成功获取到 {len(df)} 只股票数据',
                    'test_symbol': '002371',
                    'price': price
                }
                print(f"[DIAGNOSTIC] adata 成功: {price}")
            else:
                result['adata'] = {
                    'status': 'not_found',
                    'message': f'获取到 {len(df)} 只股票，但未找到 002371',
                    'test_symbol': '002371',
                    'price': None
                }
                print(f"[DIAGNOSTIC] adata 未找到股票 002371")
        else:
            result['adata'] = {
                'status': 'empty',
                'message': 'adata 返回空数据',
                'test_symbol': '002371',
                'price': None
            }
            print(f"[DIAGNOSTIC] adata 返回空数据")
    except Exception as e:
        result['adata'] = {
            'status': 'error',
            'message': f'连接失败: {str(e)}',
            'test_symbol': '002371',
            'price': None
        }
        print(f"[DIAGNOSTIC] adata 连接失败: {e}")
    
    # 测试 akshare
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        if df is not None and not df.empty:
            stock_df = df[df['代码'] == '002371']
            if not stock_df.empty:
                price = float(stock_df['最新价'].values[0])
                result['akshare'] = {
                    'status': 'success',
                    'message': f'成功获取到 {len(df)} 只股票数据',
                    'test_symbol': '002371',
                    'price': price
                }
                print(f"[DIAGNOSTIC] akshare 成功: {price}")
            else:
                result['akshare'] = {
                    'status': 'not_found',
                    'message': f'获取到 {len(df)} 只股票，但未找到 002371',
                    'test_symbol': '002371',
                    'price': None
                }
                print(f"[DIAGNOSTIC] akshare 未找到股票 002371")
        else:
            result['akshare'] = {
                'status': 'empty',
                'message': 'akshare 返回空数据',
                'test_symbol': '002371',
                'price': None
            }
            print(f"[DIAGNOSTIC] akshare 返回空数据")
    except Exception as e:
        result['akshare'] = {
            'status': 'error',
            'message': f'连接失败: {str(e)}',
            'test_symbol': '002371',
            'price': None
        }
        print(f"[DIAGNOSTIC] akshare 连接失败: {e}")
    
    # 测试 efinance
    try:
        import efinance as ef
        df = ef.stock.get_realtime_quotes()
        if df is not None and not df.empty:
            df.columns = df.columns.str.replace(' ', '')
            stock_df = df[df['股票代码'] == '002371']
            if not stock_df.empty:
                price = float(stock_df['最新价'].values[0])
                result['efinance'] = {
                    'status': 'success',
                    'message': f'成功获取到 {len(df)} 只股票数据',
                    'test_symbol': '002371',
                    'price': price
                }
                print(f"[DIAGNOSTIC] efinance 成功: {price}")
            else:
                result['efinance'] = {
                    'status': 'not_found',
                    'message': f'获取到 {len(df)} 只股票，但未找到 002371',
                    'test_symbol': '002371',
                    'price': None
                }
                print(f"[DIAGNOSTIC] efinance 未找到股票 002371")
        else:
            result['efinance'] = {
                'status': 'empty',
                'message': 'efinance 返回空数据',
                'test_symbol': '002371',
                'price': None
            }
            print(f"[DIAGNOSTIC] efinance 返回空数据")
    except Exception as e:
        result['efinance'] = {
            'status': 'error',
            'message': f'连接失败: {str(e)}',
            'test_symbol': '002371',
            'price': None
        }
        print(f"[DIAGNOSTIC] efinance 连接失败: {e}")
    
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "service": "quantitative-trading-api"
    })

@app.route('/', methods=['GET'])
def serve_index():
    import os
    # 构建前端文件的绝对路径
    current_dir = os.path.abspath(__file__)
    print(f"Current file: {current_dir}")
    parent_dir = os.path.dirname(current_dir)
    print(f"Parent directory: {parent_dir}")
    grandparent_dir = os.path.dirname(parent_dir)
    front_end_dir = os.path.join(grandparent_dir, 'web')
    index_path = os.path.join(front_end_dir, 'index.html')
    
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content, 200, {'Content-Type': 'text/html'}
    else:
        return jsonify({'error': '前端文件未找到', 'path': index_path}), 404

@app.route('/index.html', methods=['GET'])
def serve_index_html():
    return serve_index()

@app.route('/settings.html', methods=['GET'])
def serve_settings():
    import os
    # 构建前端文件的绝对路径
    current_dir = os.path.abspath(__file__)
    parent_dir = os.path.dirname(current_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    front_end_dir = os.path.join(grandparent_dir, 'web')
    settings_path = os.path.join(front_end_dir, 'settings.html')
    
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content, 200, {'Content-Type': 'text/html'}
    else:
        return jsonify({'error': '设置页面未找到', 'path': settings_path}), 404

@app.route('/plan.html', methods=['GET'])
def serve_plan():
    import os
    # 构建前端文件的绝对路径
    current_dir = os.path.abspath(__file__)
    parent_dir = os.path.dirname(current_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    front_end_dir = os.path.join(grandparent_dir, 'web')
    plan_path = os.path.join(front_end_dir, 'plan.html')
    
    if os.path.exists(plan_path):
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content, 200, {'Content-Type': 'text/html'}
    else:
        return jsonify({'error': '计划页面未找到', 'path': plan_path}), 404

@app.route('/backtest.html', methods=['GET'])
def serve_backtest():
    import os
    current_dir = os.path.abspath(__file__)
    parent_dir = os.path.dirname(current_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    front_end_dir = os.path.join(grandparent_dir, 'web')
    backtest_path = os.path.join(front_end_dir, 'backtest.html')
    
    if os.path.exists(backtest_path):
        with open(backtest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content, 200, {'Content-Type': 'text/html'}
    else:
        return jsonify({'error': '回测页面未找到', 'path': backtest_path}), 404

@app.route('/prediction.html', methods=['GET'])
def serve_prediction():
    import os
    current_dir = os.path.abspath(__file__)
    parent_dir = os.path.dirname(current_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    front_end_dir = os.path.join(grandparent_dir, 'web')
    prediction_path = os.path.join(front_end_dir, 'prediction.html')
    
    if os.path.exists(prediction_path):
        with open(prediction_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content, 200, {'Content-Type': 'text/html'}
    else:
        return jsonify({'error': '预测页面未找到', 'path': prediction_path}), 404

@app.route('/strategy.html', methods=['GET'])
def serve_strategy():
    import os
    current_dir = os.path.abspath(__file__)
    parent_dir = os.path.dirname(current_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    front_end_dir = os.path.join(grandparent_dir, 'web')
    strategy_path = os.path.join(front_end_dir, 'strategy.html')
    
    if os.path.exists(strategy_path):
        with open(strategy_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content, 200, {'Content-Type': 'text/html'}
    else:
        return jsonify({'error': '策略页面未找到', 'path': strategy_path}), 404

# PDF调度器相关API和功能
def _execute_pdf_export():
    """执行PDF导出（用于定时任务）"""
    try:
        print("开始执行定时PDF导出...")
        
        # 从配置文件获取available_cash和original_cash
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'cash_config.json')
        available_cash = 187500.00
        original_cash = 200000.00
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    available_cash = config.get('available_cash', 187500.00)
                    original_cash = config.get('original_cash', 200000.00)
                    print(f"从配置文件读取现金配置: available_cash={available_cash}, original_cash={original_cash}")
        except Exception as e:
            print(f"读取现金配置失败，使用默认值: {e}")
        
        # 在Flask应用上下文中执行所有操作
        with app.app_context():
            # 调用后端API获取持仓分析数据（与计划页面使用相同的逻辑）
            with app.test_request_context(f'/api/plan/position?available_cash={available_cash}&original_cash={original_cash}'):
                position_analysis = get_position_analysis().get_json()
            
            # 创建PDF文档
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
            
            styles = getSampleStyleSheet()
            story = []
            
            # 设置中文字体
            chinese_font = CHINESE_FONT if CHINESE_FONT else 'Helvetica'
            
            # 获取所有需要的数据
            market_status = get_market_status().get_json()
            
            adjustment_strategy = get_adjustment_strategy().get_json()
            buy_strategy = get_buy_strategy().get_json()
            news_data = get_news().get_json()
            
            # 添加标题
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=28,
                textColor=colors.HexColor('#2c3e50'),
                alignment=TA_CENTER,
                spaceAfter=30,
                fontName=chinese_font
            )
            story.append(Paragraph("每日操作计划", title_style))
            
            # 添加生成时间
            time_style = ParagraphStyle(
                'CustomTime',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName=chinese_font
            )
            story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}", time_style))
            story.append(Spacer(1, 10))
            
            # 添加分隔线
            line_style = ParagraphStyle(
                'LineStyle',
                parent=styles['Normal'],
                fontSize=1,
                leading=10
            )
            story.append(Paragraph("<hr/>", line_style))
            story.append(Spacer(1, 20))
            
            # 1. 市场状态判断
            section_style = ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=colors.HexColor('#667eea'),
                spaceBefore=15,
                spaceAfter=12,
                fontName=chinese_font
            )
            story.append(Paragraph("一、市场状态判断", section_style))
            
            status_text = market_status.get('status_text', '未知')
            status_color = colors.HexColor('#e74c3c') if market_status.get('status') == 'bull' else colors.HexColor('#27ae60')
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=8,
                fontName=chinese_font
            )
            story.append(Paragraph(f"<b>市场状态:</b> <font color='{status_color}'>{status_text}</font>", normal_style))
            story.append(Paragraph(f"<b>沪深300指数:</b> {market_status.get('hs300_index', 0):.2f}", normal_style))
            story.append(Paragraph(f"<b>120日均线:</b> {market_status.get('ma120', 0):.2f}", normal_style))
            story.append(Paragraph(f"<b>仓位建议:</b> {market_status.get('position_suggestion', '')}", normal_style))
            story.append(Spacer(1, 20))
            
            # 2. 持仓分析
            story.append(Paragraph("二、持仓分析", section_style))
            
            # 添加持仓概览信息
            overview_data = [
                ['项目', '金额'],
                ['原始资金', f"¥{position_analysis.get('original_cash', 0):,.2f}"],
                ['总资产', f"¥{position_analysis.get('total_assets', 0):,.2f}"],
                ['总盈亏', f"¥{position_analysis.get('total_profit_loss', 0):,.2f}"],
                ['持仓市值', f"¥{position_analysis.get('position_value', 0):,.2f}"],
                ['当前仓位', position_analysis.get('current_position', '0%')]
            ]
            
            overview_table = Table(overview_data, colWidths=[2.5*inch, 2.5*inch])
            overview_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), chinese_font),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(overview_table)
            story.append(Spacer(1, 20))
            
            # 添加持仓明细表格
            positions = position_analysis.get('positions', [])
            if positions:
                position_data = [['股票代码', '股票名称', '持仓数量', '成本价', '当前价', '盈亏', '盈亏率']]
                for pos in positions:
                    profit_loss = pos.get('profit_loss', 0)
                    profit_loss_percent = pos.get('profit_loss_percent', 0)
                    
                    profit_loss_color = colors.HexColor('#27ae60') if profit_loss < 0 else colors.HexColor('#e74c3c')
                    profit_loss_percent_color = colors.HexColor('#27ae60') if profit_loss_percent < 0 else colors.HexColor('#e74c3c')
                    
                    profit_loss_style = ParagraphStyle(
                        'ProfitLoss',
                        parent=styles['Normal'],
                        fontSize=10,
                        textColor=profit_loss_color,
                        alignment=TA_CENTER,
                        fontName=chinese_font
                    )
                    
                    profit_loss_percent_style = ParagraphStyle(
                        'ProfitLossPercent',
                        parent=styles['Normal'],
                        fontSize=10,
                        textColor=profit_loss_percent_color,
                        alignment=TA_CENTER,
                        fontName=chinese_font
                    )
                    
                    position_data.append([
                        pos.get('symbol', ''),
                        pos.get('name', ''),
                        str(pos.get('quantity', 0)),
                        f"{pos.get('cost_price', 0):.2f}",
                        f"{pos.get('current_price', 0):.2f}",
                        Paragraph(f"{profit_loss:.2f}", profit_loss_style),
                        Paragraph(f"{profit_loss_percent:.2f}%", profit_loss_percent_style)
                    ])
                
                table = Table(position_data, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke if i % 2 == 0 else colors.HexColor('#f5f7fa') for i in range(len(position_data) - 1)])
                ]))
                story.append(table)
            else:
                story.append(Paragraph("暂无持仓数据", normal_style))
            
            story.append(Spacer(1, 20))
            
            # 3. 调仓策略
            story.append(Paragraph("三、调仓策略", section_style))
            
            suggestions = adjustment_strategy.get('suggestions', [])
            if suggestions:
                for i, suggestion in enumerate(suggestions, 1):
                    action_text = suggestion.get('action_text', '')
                    symbol = suggestion.get('symbol', '')
                    name = suggestion.get('name', '')
                    current_price = suggestion.get('current_price', 0)
                    reason = suggestion.get('reason', '')
                    
                    action_color = colors.HexColor('#e74c3c') if suggestion.get('action') == 'sell' else colors.HexColor('#27ae60')
                    story.append(Paragraph(
                        f"{i}. <font color='{action_color}'><b>{action_text}</b></font> - {symbol} {name}",
                        normal_style
                    ))
                    story.append(Paragraph(f"   当前价格: ¥{current_price:.2f}", normal_style))
                    story.append(Paragraph(f"   原因: {reason}", normal_style))
                    story.append(Spacer(1, 12))
            else:
                story.append(Paragraph("暂无调仓建议", normal_style))
            
            story.append(Spacer(1, 20))
            
            # 4. 买入策略
            story.append(Paragraph("四、买入策略", section_style))
            
            # 获取当前持仓列表，用于过滤已持仓的股票
            held_symbols = []
            positions = position_analysis.get('positions', [])
            if positions:
                held_symbols = [pos.get('symbol', '') for pos in positions]
            
            # 过滤掉已持仓的股票
            buy_suggestions = buy_strategy.get('suggestions', [])
            filtered_suggestions = [s for s in buy_suggestions if s.get('symbol', '') not in held_symbols]
            
            if filtered_suggestions:
                for i, suggestion in enumerate(filtered_suggestions, 1):
                    symbol = suggestion.get('symbol', '')
                    name = suggestion.get('name', '')
                    price_range = suggestion.get('price_range', '')
                    stop_loss = suggestion.get('stop_loss', '')
                    reason = suggestion.get('reason', '')
                    
                    story.append(Paragraph(
                        f"{i}. <b>{symbol} {name}</b>",
                        normal_style
                    ))
                    story.append(Paragraph(f"   价格区间: {price_range}", normal_style))
                    story.append(Paragraph(f"   止损位: {stop_loss}", normal_style))
                    story.append(Paragraph(f"   原因: {reason}", normal_style))
                    story.append(Spacer(1, 12))
            else:
                story.append(Paragraph("暂无买入建议（已过滤持仓股票）", normal_style))
            
            story.append(Spacer(1, 20))
            
            # 5. 资讯整合
            story.append(Paragraph("五、资讯整合", section_style))
            
            news_list = news_data.get('news', [])
            if news_list:
                for i, news in enumerate(news_list, 1):
                    title = news.get('title', '')
                    time = news.get('time', '')
                    content = news.get('content', '')
                    
                    # 创建资讯卡片样式
                    news_box_style = ParagraphStyle(
                        'NewsBox',
                        parent=styles['Normal'],
                        fontSize=10,
                        textColor=colors.HexColor('#34495e'),
                        leftIndent=10,
                        spaceAfter=12,
                        fontName=chinese_font
                    )
                    
                    story.append(Paragraph(
                        f"<b>{i}. {title}</b> <font color='#7f8c8d'>({time})</font>",
                        news_box_style
                    ))
                    story.append(Paragraph(f"   {content}", news_box_style))
            else:
                story.append(Paragraph("暂无资讯数据", normal_style))
            
            # 添加页脚
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#95a5a6'),
                alignment=TA_CENTER,
                fontName=chinese_font
            )
            story.append(Paragraph("本报告由量化交易系统自动生成，仅供参考，不构成投资建议。", footer_style))
            
            # 生成PDF
            doc.build(story)
            buffer.seek(0)
            
            # 保存PDF文件
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scheduled_pdfs')
            os.makedirs(output_dir, exist_ok=True)
            filename = f"每日操作计划_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(buffer.getvalue())
            
            print(f"定时PDF导出成功，文件已保存至: {filepath}")
            
            return filepath
        
    except Exception as e:
        print(f"定时PDF导出失败: {e}")
        import traceback
        traceback.print_exc()
        return None

# 设置PDF调度器的回调函数
pdf_scheduler.set_pdf_export_callback(_execute_pdf_export)

# 邮件发送回调函数
def _send_email_notification(pdf_file_path: str):
    """邮件发送回调函数"""
    try:
        print(f"开始发送邮件通知: {pdf_file_path}")
        
        # 在Flask应用上下文中执行所有操作
        with app.app_context():
            # 获取市场数据用于邮件模板
            market_status = get_market_status().get_json()
            
            # 获取现金配置
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'cash_config.json')
            available_cash = 187500.00
            original_cash = 200000.00
            
            try:
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        available_cash = config.get('available_cash', 187500.00)
                        original_cash = config.get('original_cash', 200000.00)
            except Exception as e:
                print(f"读取现金配置失败，使用默认值: {e}")
            
            # 在Flask应用上下文中获取持仓分析数据
            with app.test_request_context(f'/api/plan/position?available_cash={available_cash}&original_cash={original_cash}'):
                position_analysis = get_position_analysis().get_json()
            
            market_data = {
                'market_status': market_status.get('status_text', '未知'),
                'current_position': position_analysis.get('current_position', '0%'),
                'total_assets': f"¥{position_analysis.get('total_assets', 0):,.2f}"
            }
            
            # 创建新的邮件发送器实例，确保SMTP连接
            from email_sender import EmailSender
            from email_config_manager import EmailConfigManager
            from email_template_engine import EmailTemplateEngine
            from email_logger import EmailLogger
            
            email_sender = EmailSender(
                config_manager=EmailConfigManager(),
                template_engine=EmailTemplateEngine(),
                logger=EmailLogger()
            )
            
            # 获取邮件配置并建立SMTP连接
            email_config = email_sender.config_manager.get_config()
            if email_config.get('enabled', False):
                # 确保没有其他SMTP连接
                if email_sender.smtp_connection:
                    email_sender.disconnect_smtp()
                
                # 建立新的SMTP连接
                if not email_sender.connect_smtp(email_config):
                    print(f"SMTP连接失败，无法发送邮件")
                    return
            
            # 发送邮件
            success, error_msg = email_sender.send_email(pdf_file_path, market_data)
            
            # 断开SMTP连接
            email_sender.disconnect_smtp()
            
            if success:
                print(f"邮件发送成功: {pdf_file_path}")
            else:
                print(f"邮件发送失败: {error_msg}")
            
    except Exception as e:
        print(f"邮件发送回调失败: {e}")
        import traceback
        traceback.print_exc()

# 设置邮件发送回调
pdf_scheduler.set_email_send_callback(_send_email_notification)

# API: 获取定时任务配置
@app.route('/api/scheduler/config', methods=['GET'])
def get_scheduler_config():
    config = pdf_scheduler.get_scheduled_times()
    return jsonify({
        'scheduled_times': config,
        'is_running': pdf_scheduler.is_running()
    })

# API: 设置定时任务配置
@app.route('/api/scheduler/config', methods=['POST'])
def set_scheduler_config():
    try:
        data = request.get_json()
        scheduled_times = data.get('scheduled_times', [])
        
        if not isinstance(scheduled_times, list):
            return jsonify({'error': 'scheduled_times必须是数组'}), 400
        
        for time_config in scheduled_times:
            if not isinstance(time_config, dict):
                return jsonify({'error': '每个时间配置必须是对象'}), 400
            if 'hour' not in time_config or 'minute' not in time_config:
                return jsonify({'error': '时间配置必须包含hour和minute字段'}), 400
            if not isinstance(time_config['hour'], int) or not isinstance(time_config['minute'], int):
                return jsonify({'error': 'hour和minute必须是整数'}), 400
            if time_config['hour'] < 0 or time_config['hour'] > 23:
                return jsonify({'error': 'hour必须在0-23之间'}), 400
            if time_config['minute'] < 0 or time_config['minute'] > 59:
                return jsonify({'error': 'minute必须在0-59之间'}), 400
        
        pdf_scheduler.set_scheduled_times(scheduled_times)
        
        return jsonify({
            'message': '定时任务配置已更新',
            'scheduled_times': scheduled_times
        })
    except Exception as e:
        print(f"设置定时任务配置失败: {e}")
        return jsonify({'error': f'设置失败: {str(e)}'}), 500

# API: 启动定时任务
@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    try:
        pdf_scheduler.start()
        return jsonify({
            'message': '定时任务已启动',
            'is_running': True
        })
    except Exception as e:
        print(f"启动定时任务失败: {e}")
        return jsonify({'error': f'启动失败: {str(e)}'}), 500

# API: 停止定时任务
@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    try:
        pdf_scheduler.stop()
        return jsonify({
            'message': '定时任务已停止',
            'is_running': False
        })
    except Exception as e:
        print(f"停止定时任务失败: {e}")
        return jsonify({'error': f'停止失败: {str(e)}'}), 500

# API: 获取执行记录
@app.route('/api/scheduler/execution-log', methods=['GET'])
def get_scheduler_execution_log():
    try:
        execution_log = pdf_scheduler.get_execution_log()
        return jsonify({
            'executions': execution_log
        })
    except Exception as e:
        print(f"获取执行记录失败: {e}")
        return jsonify({'error': f'获取失败: {str(e)}'}), 500

# API: 获取/设置数据更新配置
@app.route('/api/dataupdateconfig', methods=['GET', 'POST'])
def handle_data_update_config():
    print(f"收到请求: {request.method} {request.url}")
    try:
        if request.method == 'GET':
            return jsonify({
                'update_interval': pdf_scheduler.data_update_interval
            })
        elif request.method == 'POST':
            data = request.get_json()
            update_interval = data.get('update_interval')
            
            if update_interval is None:
                return jsonify({'error': 'update_interval参数不能为空'}), 400
            
            if not isinstance(update_interval, int):
                return jsonify({'error': 'update_interval必须是整数'}), 400
            
            if update_interval < 1 or update_interval > 120:
                return jsonify({'error': 'update_interval必须在1-120分钟之间'}), 400
            
            pdf_scheduler.set_data_update_interval(update_interval)
            
            return jsonify({
                'message': '数据更新配置已更新',
                'update_interval': update_interval
            })
    except Exception as e:
        print(f"处理数据更新配置失败: {e}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

# API: 测试数据库连接
@app.route('/api/email/db/test', methods=['GET'])
def test_email_db():
    try:
        # 测试数据库连接
        test_result = email_config_manager.db.test_connection()
        
        return jsonify({
            'success': True,
            'message': '数据库连接正常',
            'test_result': test_result
        })
    except Exception as e:
        print(f"测试数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'数据库连接失败: {str(e)}'
        }), 500

# API: 检查定时任务状态
@app.route('/api/scheduler/status', methods=['GET'])
def check_scheduler_status():
    try:
        status = {
            'is_running': pdf_scheduler.is_running(),
            'scheduled_times': pdf_scheduler.get_scheduled_times(),
            'execution_log': pdf_scheduler.get_execution_log()
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        print(f"检查定时任务状态失败: {e}")
        return jsonify({
            'success': False,
            'error': f'检查失败: {str(e)}'
        }), 500

# API: 获取邮件配置
@app.route('/api/email/config', methods=['GET'])
def get_email_config():
    try:
        config = email_config_manager.get_config()
        return jsonify(config)
    except Exception as e:
        print(f"获取邮件配置失败: {e}")
        return jsonify({'error': f'获取失败: {str(e)}'}), 500

# API: 设置邮件配置
@app.route('/api/email/config', methods=['POST'])
def set_email_config():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '配置数据不能为空'}), 400
        
        success = email_config_manager.update_config(data)
        
        if success:
            return jsonify({
                'message': '邮件配置已更新',
                'config': email_config_manager.get_config()
            })
        else:
            return jsonify({'error': '保存配置失败'}), 500
            
    except Exception as e:
        print(f"设置邮件配置失败: {e}")
        return jsonify({'error': f'设置失败: {str(e)}'}), 500

# API: 获取邮件模板列表
@app.route('/api/email/templates', methods=['GET'])
def get_email_templates():
    try:
        templates = email_config_manager.get_all_templates()
        return jsonify(templates)
    except Exception as e:
        print(f"获取邮件模板失败: {e}")
        return jsonify({'error': f'获取失败: {str(e)}'}), 500

# API: 获取指定邮件模板
@app.route('/api/email/templates/<template_name>', methods=['GET'])
def get_email_template(template_name):
    try:
        template = email_config_manager.get_template(template_name)
        if template:
            return jsonify(template)
        else:
            return jsonify({'error': '模板不存在'}), 404
    except Exception as e:
        print(f"获取邮件模板失败: {e}")
        return jsonify({'error': f'获取失败: {str(e)}'}), 500

# API: 保存邮件模板
@app.route('/api/email/templates', methods=['POST'])
def save_email_template():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '模板数据不能为空'}), 400
        
        template_name = data.get('template_name')
        template_type = data.get('template_type', 'text')
        subject_template = data.get('subject_template')
        body_template = data.get('body_template')
        description = data.get('description')
        
        if not template_name:
            return jsonify({'error': '模板名称不能为空'}), 400
        
        success = email_config_manager.save_template(
            template_name, template_type, subject_template, body_template, description
        )
        
        if success:
            return jsonify({
                'message': '邮件模板已保存',
                'template': email_config_manager.get_template(template_name)
            })
        else:
            return jsonify({'error': '保存模板失败'}), 500
            
    except Exception as e:
        print(f"保存邮件模板失败: {e}")
        return jsonify({'error': f'保存失败: {str(e)}'}), 500
        return jsonify({'error': f'设置失败: {str(e)}'}), 500

# API: 验证邮件配置
@app.route('/api/email/validate', methods=['POST'])
def validate_email_config():
    try:
        is_valid, error_msg = email_config_manager.validate_config()
        
        return jsonify({
            'valid': is_valid,
            'error_message': error_msg
        })
    except Exception as e:
        print(f"验证邮件配置失败: {e}")
        return jsonify({'error': f'验证失败: {str(e)}'}), 500

# API: 获取邮件发送日志
@app.route('/api/email/logs', methods=['GET'])
def get_email_logs():
    try:
        limit = request.args.get('limit', 50, type=int)
        logs = email_sender.logger.get_send_logs(limit)
        return jsonify({
            'logs': logs
        })
    except Exception as e:
        print(f"获取邮件发送日志失败: {e}")
        return jsonify({'error': f'获取失败: {str(e)}'}), 500

# API: 获取邮件发送统计
@app.route('/api/email/statistics', methods=['GET'])
def get_email_statistics():
    try:
        statistics = email_sender.logger.get_send_statistics()
        return jsonify(statistics)
    except Exception as e:
        print(f"获取邮件发送统计失败: {e}")
        return jsonify({'error': f'获取失败: {str(e)}'}), 500

# API: 发送测试邮件
@app.route('/api/email/test', methods=['POST'])
def send_test_email():
    try:
        data = request.get_json()
        recipients = data.get('recipients', [])
        
        if not recipients:
            return jsonify({'error': '接收人列表不能为空'}), 400
        
        config = email_config_manager.get_config()
        is_valid, error_msg = email_config_manager.validate_config()
        
        if not is_valid:
            return jsonify({'error': f'配置验证失败: {error_msg}'}), 400
        
        # 创建测试PDF文件
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.styles import ParagraphStyle
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        story = []
        
        # 设置中文字体
        chinese_font = CHINESE_FONT if CHINESE_FONT else 'Helvetica'
        
        # 创建使用中文字体的样式
        title_style = ParagraphStyle(
            'TestTitle',
            parent=styles['Heading1'],
            fontName=chinese_font
        )
        normal_style = ParagraphStyle(
            'TestNormal',
            parent=styles['Normal'],
            fontName=chinese_font
        )
        
        story.append(Paragraph("测试邮件", title_style))
        story.append(Paragraph("这是一封测试邮件，用于验证邮件配置是否正确。", normal_style))
        story.append(Paragraph(f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        
        doc.build(story)
        buffer.seek(0)
        
        # 保存测试PDF文件
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scheduled_pdfs')
        os.makedirs(output_dir, exist_ok=True)
        filename = f"测试邮件_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(buffer.getvalue())
        
        # 发送测试邮件
        # 重新创建EmailSender对象以获取最新配置
        from email_sender import EmailSender
        from email_template_engine import EmailTemplateEngine
        from email_logger import EmailLogger
        
        test_email_sender = EmailSender(
            config_manager=email_config_manager,
            template_engine=EmailTemplateEngine(),
            logger=EmailLogger()
        )
        
        # 建立SMTP连接
        email_config = email_config_manager.get_config()
        if email_config.get('enabled', False):
            test_email_sender.connect_smtp(email_config)
        
        success, error_msg = test_email_sender.send_email(filepath, {
            'market_status': '测试',
            'current_position': '0%',
            'total_assets': '¥0.00'
        })
        
        # 断开SMTP连接
        test_email_sender.disconnect_smtp()
        
        if success:
            return jsonify({
                'message': '测试邮件发送成功',
                'recipients': recipients
            })
        else:
            return jsonify({'error': f'发送失败: {error_msg}'}), 500
    except Exception as e:
        print(f"发送测试邮件失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'发送失败: {str(e)}'}), 500

# API: 导入接收邮箱
@app.route('/api/email/recipients/import', methods=['POST'])
def import_email_recipients():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        # 检查文件类型
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            return jsonify({'success': False, 'error': '只支持CSV和Excel文件'}), 400
        
        import pandas as pd
        
        # 读取文件
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            try:
                df = pd.read_excel(file)
            except ImportError as e:
                if 'xlrd' in str(e):
                    return jsonify({'success': False, 'error': '导入失败: xlrd 模块未安装。请联系管理员安装 xlrd>=2.0.1'}), 500
                else:
                    return jsonify({'success': False, 'error': f'导入失败: {str(e)}'}), 500
            except Exception as e:
                return jsonify({'success': False, 'error': f'导入失败: {str(e)}'}), 500
        
        # 清理列名（去除前后空格）
        df.columns = df.columns.str.strip()
        
        # 检查必要的列
        if 'email_address' not in df.columns:
            return jsonify({'success': False, 'error': '文件中缺少email_address列'}), 400
        
        # 导入数据
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                email_address = str(row['email_address']).strip()
                name = str(row.get('name', '')).strip() if 'name' in df.columns else None
                description = str(row.get('description', '')).strip() if 'description' in df.columns else None
                
                if not email_address:
                    continue
                
                success = email_config_manager.db.add_recipient(
                    email_address=email_address,
                    name=name if name else None,
                    description=description if description else None,
                    is_active=True
                )
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"第{index+2}行: 邮箱地址 {email_address} 已存在或添加失败")
            except Exception as e:
                error_count += 1
                errors.append(f"第{index+2}行: {str(e)}")
        
        print(f"邮箱导入完成: 成功 {success_count} 条，失败 {error_count} 条")
        
        return jsonify({
            'success': True,
            'message': f'导入完成，成功 {success_count} 条，失败 {error_count} 条',
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:10]  # 只返回前10个错误
        })
    except Exception as e:
        print(f"导入接收邮箱失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'导入失败: {str(e)}'}), 500

# API: 导出接收邮箱
@app.route('/api/email/recipients/export', methods=['GET'])
def export_email_recipients():
    try:
        import pandas as pd
        from io import BytesIO
        
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        recipients = email_config_manager.db.get_recipients(active_only)
        
        if not recipients:
            return jsonify({'success': False, 'error': '没有数据可导出'}), 400
        
        # 转换为DataFrame
        df = pd.DataFrame(recipients)
        # 移除不需要的列
        if 'id' in df.columns:
            df = df.drop('id', axis=1)
        
        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='接收邮箱列表')
        
        output.seek(0)
        
        from flask import send_file
        return send_file(
            output,
            as_attachment=True,
            download_name=f'接收邮箱列表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"导出接收邮箱失败: {e}")
        return jsonify({'success': False, 'error': f'导出失败: {str(e)}'}), 500

# API: 获取接收邮箱列表
@app.route('/api/email/recipients', methods=['GET'])
def get_email_recipients():
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        recipients = email_config_manager.db.get_recipients(active_only)
        return jsonify({'success': True, 'data': recipients})
    except Exception as e:
        print(f"获取接收邮箱列表失败: {e}")
        return jsonify({'success': False, 'error': f'获取失败: {str(e)}'}), 500

# API: 添加接收邮箱
@app.route('/api/email/recipients', methods=['POST'])
def add_email_recipient():
    try:
        data = request.get_json()
        email_address = data.get('email_address')
        name = data.get('name')
        description = data.get('description')
        is_active = data.get('is_active', True)
        
        if not email_address:
            return jsonify({'success': False, 'error': '邮箱地址不能为空'}), 400
        
        # 简单的邮箱格式验证
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email_address):
            return jsonify({'success': False, 'error': '邮箱地址格式不正确'}), 400
        
        success = email_config_manager.db.add_recipient(
            email_address=email_address,
            name=name,
            description=description,
            is_active=is_active
        )
        
        if success:
            return jsonify({'success': True, 'message': '添加成功'})
        else:
            return jsonify({'success': False, 'error': '邮箱地址已存在'}), 400
    except Exception as e:
        print(f"添加接收邮箱失败: {e}")
        return jsonify({'success': False, 'error': f'添加失败: {str(e)}'}), 500

# API: 更新接收邮箱
@app.route('/api/email/recipients/<int:recipient_id>', methods=['PUT'])
def update_email_recipient(recipient_id):
    try:
        data = request.get_json()
        email_address = data.get('email_address')
        name = data.get('name')
        description = data.get('description')
        is_active = data.get('is_active')
        
        # 如果提供了邮箱地址，进行格式验证
        if email_address:
            import re
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email_address):
                return jsonify({'success': False, 'error': '邮箱地址格式不正确'}), 400
        
        success = email_config_manager.db.update_recipient(
            id=recipient_id,
            email_address=email_address,
            name=name,
            description=description,
            is_active=is_active
        )
        
        if success:
            return jsonify({'success': True, 'message': '更新成功'})
        else:
            return jsonify({'success': False, 'error': '更新失败，可能邮箱地址已存在'}), 400
    except Exception as e:
        print(f"更新接收邮箱失败: {e}")
        return jsonify({'success': False, 'error': f'更新失败: {str(e)}'}), 500

# API: 删除接收邮箱
@app.route('/api/email/recipients/<int:recipient_id>', methods=['DELETE'])
def delete_email_recipient(recipient_id):
    try:
        success = email_config_manager.db.delete_recipient(recipient_id)
        
        if success:
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            return jsonify({'success': False, 'error': '删除失败'}), 400
    except Exception as e:
        print(f"删除接收邮箱失败: {e}")
        return jsonify({'success': False, 'error': f'删除失败: {str(e)}'}), 500

# API: 清空接收邮箱列表
@app.route('/api/email/recipients', methods=['DELETE'])
def clear_email_recipients():
    try:
        success = email_config_manager.db.clear_recipients()
        
        if success:
            return jsonify({'success': True, 'message': '清空成功'})
        else:
            return jsonify({'success': False, 'error': '清空失败'}), 400
    except Exception as e:
        print(f"清空接收邮箱失败: {e}")
        return jsonify({'success': False, 'error': f'清空失败: {str(e)}'}), 500
            
# API: 测试路由
@app.route('/api/test', methods=['GET', 'POST'])
def test_route():
    return jsonify({'message': 'Test route works', 'method': request.method})

# API: 获取数据更新日志
@app.route('/api/dataupdatelog', methods=['GET'])
def get_data_update_log():
    try:
        log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'data_update_log.json')
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                return jsonify({'logs': logs[-50:]})
        else:
            return jsonify({'logs': []})
    except Exception as e:
        print(f"获取数据更新日志失败: {e}")
        return jsonify({'error': f'获取失败: {str(e)}'}), 500

# API: 获取可用现金配置
@app.route('/api/config/available_cash', methods=['GET'])
def get_available_cash_config():
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'cash_config.json')
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return jsonify(config)
        else:
            return jsonify({
                'available_cash': 187500.00,
                'original_cash': 200000.00
            })
    except Exception as e:
        print(f"读取现金配置失败: {e}")
        return jsonify({
            'available_cash': 187500.00,
            'original_cash': 200000.00
        })

# API: 设置可用现金配置
@app.route('/api/config/available_cash', methods=['POST'])
def set_available_cash_config():
    try:
        data = request.get_json()
        available_cash = data.get('available_cash')
        original_cash = data.get('original_cash')
        
        config = {
            'available_cash': float(available_cash) if available_cash is not None else 187500.00,
            'original_cash': float(original_cash) if original_cash is not None else 200000.00
        }
        
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'cash_config.json')
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"现金配置已保存: {config}")
        return jsonify({
            'message': '现金配置已更新',
            'config': config
        })
    except Exception as e:
        print(f"设置现金配置失败: {e}")
        return jsonify({'error': f'设置失败: {str(e)}'}), 500

# 404错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

# 数据更新回调函数
def update_market_status_data():
    """更新市场状态数据"""
    try:
        print("开始更新市场状态数据...")
        with app.test_request_context():
            response = get_market_status()
            if response.status_code == 200:
                pdf_scheduler.log_data_update('市场状态判断', True)
                print("市场状态数据更新成功")
            else:
                pdf_scheduler.log_data_update('市场状态判断', False, f"HTTP状态码: {response.status_code}")
    except Exception as e:
        pdf_scheduler.log_data_update('市场状态判断', False, str(e))
        print(f"更新市场状态数据失败: {e}")

def update_position_analysis_data():
    """更新持仓分析数据"""
    try:
        print("开始更新持仓分析数据...")
        
        # 获取实时股票价格并更新到持仓文件
        position_file = get_position_file_path()
        if os.path.exists(position_file):
            print(f"从文件读取持仓数据: {position_file}")
            with open(position_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                positions = list(reader)
            
            # 更新每只股票的实时价格
            updated_positions = []
            for pos in positions:
                try:
                    symbol = pos['symbol']
                    name = pos['name']
                    quantity = int(pos['quantity'])
                    cost_price = float(pos['cost_price'])
                    
                    # 获取实时股票价格
                    current_price = DataProvider.get_current_price(symbol)
                    
                    if current_price is not None and current_price > 0:
                        print(f"获取到 {symbol} ({name}) 实时价格: {current_price}")
                        # 使用实时价格
                        pos['current_price'] = str(current_price)
                    else:
                        # 如果获取失败，保持原价格
                        current_price = float(pos['current_price'])
                        print(f"获取 {symbol} ({name}) 实时价格失败，使用文件中的价格: {current_price}")
                    
                    # 重新计算盈亏和盈亏百分比
                    profit_loss = (current_price - cost_price) * quantity
                    profit_loss_percent = (profit_loss / (cost_price * quantity)) * 100 if cost_price > 0 else 0
                    
                    pos['profit_loss'] = str(profit_loss)
                    pos['profit_loss_percent'] = str(profit_loss_percent)
                    updated_positions.append(pos)
                    
                except Exception as e:
                    print(f"处理持仓数据失败: {e}")
                    updated_positions.append(pos)
            
            # 保存更新后的数据回文件
            with open(position_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['symbol', 'name', 'quantity', 'cost_price', 'current_price', 'profit_loss', 'profit_loss_percent']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_positions)
            print(f"持仓数据已更新并保存: {position_file}")
        
        with app.test_request_context():
            response = get_position_analysis()
            if response.status_code == 200:
                pdf_scheduler.log_data_update('持仓分析', True)
                print("持仓分析数据更新成功")
            else:
                pdf_scheduler.log_data_update('持仓分析', False, f"HTTP状态码: {response.status_code}")
    except Exception as e:
        pdf_scheduler.log_data_update('持仓分析', False, str(e))
        print(f"更新持仓分析数据失败: {e}")

def update_adjustment_strategy_data():
    """更新调仓策略数据"""
    try:
        print("开始更新调仓策略数据...")
        with app.test_request_context():
            response = get_adjustment_strategy()
            if response.status_code == 200:
                pdf_scheduler.log_data_update('调仓策略', True)
                print("调仓策略数据更新成功")
            else:
                pdf_scheduler.log_data_update('调仓策略', False, f"HTTP状态码: {response.status_code}")
    except Exception as e:
        pdf_scheduler.log_data_update('调仓策略', False, str(e))
        print(f"更新调仓策略数据失败: {e}")

def update_buy_strategy_data():
    """更新买入策略数据"""
    try:
        print("开始更新买入策略数据...")
        with app.test_request_context():
            response = get_buy_strategy()
            if response.status_code == 200:
                pdf_scheduler.log_data_update('买入策略', True)
                print("买入策略数据更新成功")
            else:
                pdf_scheduler.log_data_update('买入策略', False, f"HTTP状态码: {response.status_code}")
    except Exception as e:
        pdf_scheduler.log_data_update('买入策略', False, str(e))
        print(f"更新买入策略数据失败: {e}")

# 注册数据更新回调函数
def register_data_update_callbacks():
    """注册所有数据更新回调函数"""
    pdf_scheduler.add_data_update_callback(update_market_status_data)
    pdf_scheduler.add_data_update_callback(update_position_analysis_data)
    pdf_scheduler.add_data_update_callback(update_adjustment_strategy_data)
    pdf_scheduler.add_data_update_callback(update_buy_strategy_data)
    print("数据更新回调函数已注册")

def run_app():
    """运行Flask应用"""
    os.makedirs(LOG_DIR, exist_ok=True)
    
    print("后端服务器启动中...")
    print("注册的路由:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            print(f"  {rule}")
    print("\n服务器运行在 http://0.0.0.0:5006")
    print("按 Ctrl+C 停止服务器")
    
    # 注册数据更新回调函数
    register_data_update_callbacks()
    
    # 设置邮件发送回调
    pdf_scheduler.set_email_send_callback(_send_email_notification)
    
    # 启动PDF定时任务调度器
    print("正在启动PDF定时任务调度器...")
    pdf_scheduler.start()
    
    # 确认定时任务已启动
    if pdf_scheduler.is_running():
        print("✅ PDF定时任务调度器启动成功")
        scheduled_times = pdf_scheduler.get_scheduled_times()
        time_strs = [f"{t['hour']:02d}:{t['minute']:02d}" for t in scheduled_times]
        print(f"定时执行时间: {time_strs}")
    else:
        print("❌ PDF定时任务调度器启动失败")
    
    app.run(host='0.0.0.0', port=5006, debug=False, threaded=True)

if __name__ == '__main__':
    run_app()