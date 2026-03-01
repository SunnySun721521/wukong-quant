import baostock as bs
import pandas as pd
from datetime import datetime, timedelta

def check_ningde_times():
    """检查宁德时代（300750）是否符合牛回踩策略买入条件"""
    
    symbol = "300750"
    name = "宁德时代"
    
    print(f"检查股票: {symbol} {name}")
    print("=" * 60)
    
    # 登录baostock
    try:
        lg = bs.login()
        if lg.error_code != '0':
            print(f"baostock登录失败: {lg.error_msg}")
            return
        print("baostock登录成功")
    except Exception as e:
        print(f"baostock登录异常: {e}")
        return
    
    # 获取最近365天的数据
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        print(f"获取数据时间范围: {start_date} 至 {end_date}")
        
        rs = bs.query_history_k_data_plus(
            f"sz.{symbol}",
            "date,code,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="3"
        )
        
        if rs.error_code != '0':
            print(f"获取K线数据失败: {rs.error_msg}")
            bs.logout()
            return
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        print(f"获取到 {len(data_list)} 天数据")
        
        if len(data_list) < 200:
            print(f"数据量不足，需要至少200天数据，当前只有{len(data_list)}天")
            bs.logout()
            return
        
        df = pd.DataFrame(data_list, columns=['date', 'code', 'open', 'high', 'low', 'close', 'volume'])
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        # 获取最新价格和成交量
        current_price = float(df.iloc[-1]['close'])
        volume = float(df.iloc[-1]['volume'])
        latest_date = df.iloc[-1]['date']
        
        print(f"\n最新数据 ({latest_date}):")
        print(f"  当前价格: {current_price}")
        print(f"  成交量: {volume}")
        
        # 计算均线
        ma20 = float(df['close'].tail(20).mean())
        ma250 = float(df['close'].tail(250).mean()) if len(df) >= 250 else float(df['close'].tail(len(df)).mean())
        v_ma5 = float(df['volume'].tail(5).mean())
        v_ma60 = float(df['volume'].tail(60).mean())
        
        print(f"\n均线指标:")
        print(f"  MA20 (20日均线): {ma20}")
        print(f"  MA250 (250日均线/年线): {ma250}")
        print(f"  V_MA5 (5日均量): {v_ma5}")
        print(f"  V_MA60 (60日均量): {v_ma60}")
        
        # 检查基础条件
        print(f"\n基础条件检查:")
        condition1 = current_price > ma250
        print(f"  1. 当前价格 > 年线 (MA250): {current_price} > {ma250} = {condition1}")
        
        condition2 = v_ma5 > v_ma60
        print(f"  2. 5日均量 > 60日均量: {v_ma5} > {v_ma60} = {condition2}")
        
        base_condition = condition1 and condition2
        print(f"  基础条件是否满足: {base_condition}")
        
        # 检查信号条件
        print(f"\n信号条件检查:")
        
        shrink_volume = volume < v_ma5 * 0.8
        print(f"  3. 缩量 (成交量 < 5日均量的80%): {volume} < {v_ma5 * 0.8} = {shrink_volume}")
        
        backtest_ma20 = abs(current_price / ma20 - 1) < 0.015
        price_deviation = abs(current_price / ma20 - 1) * 100
        print(f"  4. 回踩20日线 (收盘价在20日均线上下1.5%范围内):")
        print(f"     价格偏离度: {price_deviation:.2f}%")
        print(f"     条件: {price_deviation:.2f}% < 1.5% = {backtest_ma20}")
        
        signal_condition = shrink_volume and backtest_ma20
        print(f"  信号条件是否满足: {signal_condition}")
        
        # 总体判断
        print(f"\n总体判断:")
        all_conditions = base_condition and signal_condition
        print(f"  是否符合牛回踩买入策略: {all_conditions}")
        
        if not all_conditions:
            print(f"\n不符合原因:")
            if not condition1:
                print(f"  ✗ 当前价格 ({current_price}) 低于年线 ({ma250})")
            if not condition2:
                print(f"  ✗ 5日均量 ({v_ma5}) 不大于60日均量 ({v_ma60})")
            if not shrink_volume:
                print(f"  ✗ 成交量 ({volume}) 未缩量，不小于5日均量的80% ({v_ma5 * 0.8})")
            if not backtest_ma20:
                print(f"  ✗ 价格偏离20日线过大 ({price_deviation:.2f}%)，超过1.5%范围")
        
        # 计算价格区间和止损位
        if all_conditions:
            price_range = f"{round(current_price * 0.98, 2)}-{round(current_price * 1.02, 2)}"
            stop_loss = round(current_price * 0.96, 2)
            print(f"\n买入建议:")
            print(f"  建议价格区间: {price_range}")
            print(f"  止损位: {stop_loss}")
        
    except Exception as e:
        print(f"分析过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bs.logout()
        print("\nbaostock已登出")

if __name__ == "__main__":
    check_ningde_times()
