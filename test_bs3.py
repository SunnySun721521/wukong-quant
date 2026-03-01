# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd
import sys

try:
    lg = bs.login()
    print(f"login: {lg.error_code}", flush=True)
    
    rs = bs.query_history_k_data_plus(
        "sz.002009",
        "date,close",
        start_date="2019-01-01",
        end_date="2020-12-31",
        frequency="d",
        adjustflag="3"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    print(f"data rows: {len(data_list)}", flush=True)
    
    df = pd.DataFrame(data_list, columns=['date', 'close'])
    df['date'] = pd.to_datetime(df['date'])
    df['close'] = pd.to_numeric(df['close'])
    df['ma250'] = df['close'].rolling(window=250).mean()
    
    first_valid = None
    for i, row in df.iterrows():
        if not pd.isna(row['ma250']):
            first_valid = row['date']
            print(f"first valid ma250: {row['date'].date()}, value={row['ma250']:.2f}", flush=True)
            break
    
    if first_valid:
        print("\n=== data with valid ma250 ===", flush=True)
        for i, row in df.iterrows():
            if row['date'] >= first_valid and row['date'] <= pd.Timestamp('2020-08-15'):
                print(f"{row['date'].date()}, close={row['close']:.2f}, ma250={row['ma250']:.2f}" if not pd.isna(row['ma250']) else f"{row['date'].date()}, close={row['close']:.2f}, ma250=N/A", flush=True)
    
    bs.logout()
    print("done", flush=True)
except Exception as e:
    print(f"error: {e}", flush=True)
    import traceback
    traceback.print_exc()
