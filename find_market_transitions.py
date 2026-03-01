#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'strategy'))
from data_provider import DataProvider

# 加载沪深300数据
hs300_df = DataProvider.load_hs300_data()
if hs300_df is not None and not hs300_df.empty:
    hs300_df['ma120'] = hs300_df['close'].rolling(window=120).mean()
    
    # 查找市场状态转换点
    transitions = []
    prev_state = None
    for i in range(len(hs300_df)):
        if pd.isna(hs300_df.iloc[i]['ma120']):
            continue
        current_state = '牛' if hs300_df.iloc[i]['close'] > hs300_df.iloc[i]['ma120'] else '熊'
        if prev_state is not None and prev_state != current_state:
            transitions.append({
                'date': hs300_df.index[i].date(),
                'from': prev_state,
                'to': current_state,
                'close': hs300_df.iloc[i]['close'],
                'ma120': hs300_df.iloc[i]['ma120']
            })
        prev_state = current_state
    
    print(f'找到 {len(transitions)} 次市场状态转换：')
    for t in transitions:
        print(f"{t['date']}: {t['from']} -> {t['to']} (close={t['close']:.2f}, ma120={t['ma120']:.2f})")
