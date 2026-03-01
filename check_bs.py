# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd

lines = []
lines.append("Starting...")

try:
    lg = bs.login()
    lines.append(f"Login: {lg.error_code}")
    
    symbol = "sz.002009"
    start_date = "2018-01-01"
    end_date = "2020-08-31"
    
    rs = bs.query_history_k_data_plus(
        symbol, "date,open,high,low,close,volume",
        start_date=start_date, end_date=end_date,
        frequency="d", adjustflag="3"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    lines.append(f"Data rows: {len(data_list)}")
    
    if len(data_list) > 0:
        df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma250'] = df['close'].rolling(250).mean()
        df['v_ma5'] = df['volume'].rolling(5).mean()
        df['v_ma60'] = df['volume'].rolling(60).mean()
        
        high = df['high']; low = df['low']; close = df['close']
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = tr.rolling(20).mean()
        
        lines.append("\n=== 2020-08-03 ===")
        d1 = pd.Timestamp('2020-08-03')
        if d1 in df.index:
            r = df.loc[d1]
            lines.append(f"Close: {r['close']}")
            lines.append(f"MA250: {r['ma250']}")
            lines.append(f"V_MA5: {r['v_ma5']}")
            lines.append(f"V_MA60: {r['v_ma60']}")
            if pd.notna(r['ma250']):
                c1 = r['close'] > r['ma250']
                c2 = r['v_ma5'] > r['v_ma60']
                c3 = r['volume'] < r['v_ma5'] * 0.8
                c4 = abs(r['close'] / r['ma20'] - 1) < 0.015
                lines.append(f"Buy cond1 (close>ma250): {c1}")
                lines.append(f"Buy cond2 (v_ma5>v_ma60): {c2}")
                lines.append(f"Buy cond3 (shrink): {c3}")
                lines.append(f"Buy cond4 (backtest ma20): {c4}")
                lines.append(f"BUY SIGNAL: {c1 and c2 and c3 and c4}")
        
        lines.append("\n=== 2020-08-04 ===")
        d2 = pd.Timestamp('2020-08-04')
        if d2 in df.index:
            r = df.loc[d2]
            lines.append(f"Close: {r['close']}")
            lines.append(f"MA250: {r['ma250']}")
            lines.append(f"V_MA5: {r['v_ma5']}")
            lines.append(f"V_MA60: {r['v_ma60']}")
            if pd.notna(r['ma250']):
                c1 = r['close'] > r['ma250']
                c2 = r['v_ma5'] > r['v_ma60']
                c3 = r['volume'] < r['v_ma5'] * 0.8
                c4 = abs(r['close'] / r['ma20'] - 1) < 0.015
                lines.append(f"Buy cond1 (close>ma250): {c1}")
                lines.append(f"Buy cond2 (v_ma5>v_ma60): {c2}")
                lines.append(f"Buy cond3 (shrink): {c3}")
                lines.append(f"Buy cond4 (backtest ma20): {c4}")
                lines.append(f"BUY SIGNAL: {c1 and c2 and c3 and c4}")
    
    bs.logout()
    lines.append("Done")
    
except Exception as e:
    lines.append(f"Error: {e}")

with open("d:/trae/备份悟空52224/result_bs.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Done")
