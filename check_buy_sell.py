# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd

lg = bs.login()
print(f"登录: {lg.error_code}")

# 获取足够的历史数据（从2018年开始，确保有250日均线数据）
symbol = "sz.002009"
start_date = "2018-01-01"
end_date = "2020-08-31"

rs = bs.query_history_k_data_plus(
    symbol,
    "date,open,high,low,close,volume",
    start_date=start_date,
    end_date=end_date,
    frequency="d",
    adjustflag="3"
)

data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())

print(f"获取到 {len(data_list)} 条数据")

df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

for col in ['open', 'high', 'low', 'close', 'volume']:
    df[col] = pd.to_numeric(df[col])

# 计算指标
df['ma20'] = df['close'].rolling(window=20).mean()
df['ma250'] = df['close'].rolling(window=250).mean()
df['v_ma5'] = df['volume'].rolling(window=5).mean()
df['v_ma60'] = df['volume'].rolling(window=60).mean()

# ATR计算
high = df['high']
low = df['low']
close = df['close']
tr1 = high - low
tr2 = abs(high - close.shift(1))
tr3 = abs(low - close.shift(1))
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
df['atr'] = tr.rolling(window=20).mean()

# 查看2020-08-03和2020-08-04的数据
print("\n" + "="*80)
print("2020年8月3日和8月4日数据:")
print("="*80)

for date_str in ['2020-08-03', '2020-08-04']:
    date = pd.Timestamp(date_str)
    if date in df.index:
        row = df.loc[date]
        print(f"\n日期: {date_str}")
        print(f"  开盘: {row['open']:.2f}")
        print(f"  收盘: {row['close']:.2f}")
        print(f"  最高: {row['high']:.2f}")
        print(f"  最低: {row['low']:.2f}")
        print(f"  成交量: {row['volume']:.0f}")
        print(f"  MA20: {row['ma20']:.2f}" if pd.notna(row['ma20']) else "  MA20: N/A")
        print(f"  MA250: {row['ma250']:.2f}" if pd.notna(row['ma250']) else "  MA250: N/A")
        print(f"  V_MA5: {row['v_ma5']:.0f}" if pd.notna(row['v_ma5']) else "  V_MA5: N/A")
        print(f"  V_MA60: {row['v_ma60']:.0f}" if pd.notna(row['v_ma60']) else "  V_MA60: N/A")
        print(f"  ATR: {row['atr']:.2f}" if pd.notna(row['atr']) else "  ATR: N/A")

        # 检查买入条件
        print(f"\n  买入条件检查:")
        if pd.notna(row['ma250']) and pd.notna(row['ma250']):
            cond1 = row['close'] > row['ma250']
            print(f"    1. 收盘价 > MA250: {cond1} ({row['close']:.2f} > {row['ma250']:.2f})")
            
            cond2 = row['v_ma5'] > row['v_ma60']
            print(f"    2. V_MA5 > V_MA60: {cond2} ({row['v_ma5']:.0f} > {row['v_ma60']:.0f})")
            
            cond3 = row['volume'] < row['v_ma5'] * 0.8
            print(f"    3. 缩量 (volume < V_MA5*0.8): {cond3} ({row['volume']:.0f} < {row['v_ma5']*0.8:.0f})")
            
            cond4 = abs(row['close'] / row['ma20'] - 1) < 0.015
            print(f"    4. 回踩MA20 (|close/MA20-1| < 0.015): {cond4} ({abs(row['close'] / row['ma20'] - 1)*100:.2f}%)")
            
            buy_signal = cond1 and cond2 and cond3 and cond4
            print(f"\n  => 买入信号: {'✅ 是' if buy_signal else '❌ 否'}")
            
            # 检查卖出条件（跌破MA250）
            prev_date = date - pd.Timedelta(days=1)
            while prev_date not in df.index and prev_date > pd.Timestamp('2020-01-01'):
                prev_date = prev_date - pd.Timedelta(days=1)
            
            if prev_date in df.index:
                prev_close = df.loc[prev_date, 'close']
                prev_ma250 = df.loc[prev_date, 'ma250']
                if pd.notna(prev_close) and pd.notna(prev_ma250):
                    sell_signal = prev_close > prev_ma250 and row['close'] < row['ma250']
                    print(f"  => 卖出信号(跌破MA250): {'✅ 是' if sell_signal else '❌ 否'}")
        else:
            print(f"  MA250数据不足，无法计算")

bs.logout()
