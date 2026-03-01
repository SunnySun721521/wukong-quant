        print(f"牛回踩ATR策略: df长度={len(df)}, 需要至少250天数据")

        df['signal'] = 0
        df['trailing_stop'] = 0.0
        
        for i in range(250, len(df)):
            if pd.isna(df['atr'].iloc[i]) or pd.isna(df['ma250'].iloc[i]):
                df['signal'].iloc[i] = df['signal'].iloc[i-1] if i > 0 else 0
                df['trailing_stop'].iloc[i] = df['trailing_stop'].iloc[i-1] if i > 0 else 0
                continue
            
            buy_condition = (
                df['close'].iloc[i] > df['ma250'].iloc[i] and
                df['v_ma5'].iloc[i] > df['v_ma60'].iloc[i] and
                df['volume'].iloc[i] < df['v_ma5'].iloc[i] * 0.8 and
                abs(df['close'].iloc[i] / df['ma20'].iloc[i] - 1) < 0.015
            )
            
            if buy_condition:
                df['signal'].iloc[i] = 1
                if df['signal'].iloc[i-1] == 0:
                    df['trailing_stop'].iloc[i] = df['high'].iloc[i] - 4 * df['atr'].iloc[i]
                else:
                    prev_trailing = df['trailing_stop'].iloc[i-1] if i > 0 else 0
                    highest_since_entry = df['high'].iloc[i]
                    for j in range(i-1, -1, -1):
                        if df['signal'].iloc[j] == 0:
                            break
                        highest_since_entry = max(highest_since_entry, df['high'].iloc[j])
                    df['trailing_stop'].iloc[i] = max(highest_since_entry - 4 * df['atr'].iloc[i], prev_trailing)
            else:
                current_trailing = df['trailing_stop'].iloc[i-1] if i > 0 else 0
                if current_trailing > 0 and df['close'].iloc[i] < current_trailing:
                    df['signal'].iloc[i] = 0
                else:
                    df['signal'].iloc[i] = df['signal'].iloc[i-1] if i > 0 else 0
                df['trailing_stop'].iloc[i] = current_trailing

            if df['close'].iloc[i] < df['ma250'].iloc[i]:
                df['signal'].iloc[i] = 0
                df['trailing_stop'].iloc[i] = 0

        df['position'] = df['signal'].diff()
        df['position'] = df['position'].fillna(0)
        print(f"牛回踩ATR策略: 买入信号={(df['position'] == 1).sum()}, 卖出信号={(df['position'] == -1).sum()}")
        return df
