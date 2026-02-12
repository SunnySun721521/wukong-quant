import baostock as bs
from datetime import datetime, timedelta
import pandas as pd

lg = bs.login()
print(f"登录结果: error_code={lg.error_code}, error_msg={lg.error_msg}")

if lg.error_code == '0':
    symbol = "600170"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    rs = bs.query_history_k_data_plus(
        f"sh.{symbol}",
        "date,code,open,high,low,close,volume",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="3"
    )
    
    print(f"查询结果: error_code={rs.error_code}, error_msg={rs.error_msg}")
    
    if rs.error_code == '0':
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        print(f"获取到 {len(data_list)} 天数据")
        
        if len(data_list) >= 200:
            df = pd.DataFrame(data_list, columns=['date', 'code', 'open', 'high', 'low', 'close', 'volume'])
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            
            current_price = float(df.iloc[-1]['close'])
            volume = float(df.iloc[-1]['volume'])
            ma20 = float(df['close'].tail(20).mean())
            ma250 = float(df['close'].tail(250).mean()) if len(df) >= 250 else float(df['close'].tail(len(df)).mean())
            v_ma5 = float(df['volume'].tail(5).mean())
            v_ma60 = float(df['volume'].tail(60).mean())
            
            print(f"价格: {current_price}, MA20: {ma20}, MA250: {ma250}, 成交量: {volume}, V_MA5: {v_ma5}, V_MA60: {v_ma60}")
            
            base_condition = current_price > ma250 and v_ma5 > v_ma60
            shrink_volume = volume < v_ma5 * 0.8
            backtest_ma20 = abs(current_price / ma20 - 1) < 0.015
            signal_condition = shrink_volume and backtest_ma20
            
            print(f"基础条件: {base_condition}, 信号条件: {signal_condition}")
            print(f"符合买入条件: {base_condition and signal_condition}")
    
    bs.logout()
else:
    print("baostock登录失败")
