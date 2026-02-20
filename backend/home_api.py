import os
import json
import time

HOME_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'home_cache.json')
HOME_CACHE = {}
HOME_CACHE_EXPIRE = 300

def load_home_cache():
    global HOME_CACHE
    try:
        if os.path.exists(HOME_CACHE_FILE):
            with open(HOME_CACHE_FILE, 'r', encoding='utf-8') as f:
                HOME_CACHE = json.load(f)
    except:
        HOME_CACHE = {}

def save_home_cache():
    try:
        os.makedirs(os.path.dirname(HOME_CACHE_FILE), exist_ok=True)
        with open(HOME_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(HOME_CACHE, f, ensure_ascii=False, indent=2)
    except:
        pass

load_home_cache()

def get_home_overview_optimized():
    """
    优化后的首页组合总体表现API
    - 使用缓存价格，不调用baostock
    - 不运行回测，使用简化计算
    - 添加API响应缓存
    """
    from datetime import datetime
    import csv
    
    print("API called: /api/home/overview (optimized)")
    
    cache_key = 'home_overview'
    if cache_key in HOME_CACHE:
        cached = HOME_CACHE[cache_key]
        if time.time() - cached.get('timestamp', 0) < HOME_CACHE_EXPIRE:
            print("返回缓存的首页数据")
            return cached.get('data')
    
    try:
        INITIAL_CASH = 200000.0
        
        start_date = '2026-01-01'
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        position_file = get_position_file_path()
        positions = []
        
        if os.path.exists(position_file):
            with open(position_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                positions = list(reader)
        
        position_value = 0.0
        total_cost = 0.0
        updated_positions = []
        
        for pos in positions:
            try:
                symbol = pos['symbol']
                name = pos['name']
                quantity = int(pos['quantity'])
                cost_price = float(pos['cost_price'])
                current_price = float(pos['current_price'])
                
                cached_price = get_cached_price(symbol)
                if cached_price:
                    current_price = cached_price
                
                profit_loss = (current_price - cost_price) * quantity
                profit_loss_percent = (profit_loss / (cost_price * quantity)) * 100 if cost_price > 0 else 0
                
                position_value += current_price * quantity
                total_cost += cost_price * quantity
                
                updated_positions.append({
                    'symbol': symbol,
                    'name': name,
                    'quantity': quantity,
                    'cost_price': cost_price,
                    'current_price': current_price,
                    'profit_loss': round(profit_loss, 2),
                    'profit_loss_percent': round(profit_loss_percent, 2),
                    'market_value': round(current_price * quantity, 2)
                })
                
            except Exception as e:
                print(f"处理股票 {pos.get('symbol')} 数据失败: {e}")
                quantity = int(pos.get('quantity', 0))
                cost_price = float(pos.get('cost_price', 0))
                current_price = float(pos.get('current_price', 0))
                position_value += current_price * quantity
                total_cost += cost_price * quantity
                updated_positions.append({
                    'symbol': pos.get('symbol'),
                    'name': pos.get('name'),
                    'quantity': quantity,
                    'cost_price': cost_price,
                    'current_price': current_price,
                    'profit_loss': float(pos.get('profit_loss', 0)),
                    'profit_loss_percent': float(pos.get('profit_loss_percent', 0)),
                    'market_value': round(current_price * quantity, 2)
                })
        
        cash_config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'cash_config.json')
        available_cash = 187500.0
        if os.path.exists(cash_config_file):
            try:
                with open(cash_config_file, 'r', encoding='utf-8') as f:
                    cash_config = json.load(f)
                    available_cash = cash_config.get('available_cash', 187500.0)
            except:
                pass
        
        final_value = available_cash + position_value
        total_return = (final_value - INITIAL_CASH) / INITIAL_CASH * 100
        
        max_drawdown = 0.0
        total_trades = len(updated_positions) * 2
        win_trades = sum(1 for p in updated_positions if p.get('profit_loss', 0) > 0)
        win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
        
        if total_cost > 0 and position_value > 0:
            if total_return < 0:
                max_drawdown = abs(total_return) * 0.5
        
        result = {
            'initial_cash': INITIAL_CASH,
            'final_value': round(final_value, 2),
            'total_return': round(total_return, 2),
            'max_drawdown': round(max_drawdown, 2),
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'available_cash': round(available_cash, 2),
            'position_value': round(position_value, 2),
            'start_date': start_date,
            'end_date': end_date,
            'positions': updated_positions,
            'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        HOME_CACHE[cache_key] = {
            'data': result,
            'timestamp': time.time()
        }
        save_home_cache()
        
        print(f"首页数据返回: final_value={final_value}, total_return={total_return}%")
        return result
        
    except Exception as e:
        print(f"获取首页数据失败: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

def get_position_file_path():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'positions.csv')

def get_cached_price(symbol):
    from app import PRICE_CACHE
    if symbol in PRICE_CACHE:
        cached = PRICE_CACHE[symbol]
        if time.time() - cached.get('timestamp', 0) < 86400:
            return cached.get('price')
    return None
