import baostock as bs
import pandas as pd
from datetime import datetime, timedelta

print("测试 BaoStock 连接...")

try:
    lg = bs.login()
    print(f"登录结果: error_code={lg.error_code}, error_msg={lg.error_msg}")
    
    if lg.error_code == '0':
        print("登录成功！")
        
        # 获取最近120天的沪深300数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=150)).strftime("%Y-%m-%d")
        
        print(f"获取沪深300数据: {start_date} 到 {end_date}")
        
        rs = bs.query_history_k_data_plus(
            "sh.000300",
            "date,open,high,low,close,volume",
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
            
            print(f"成功获取 {len(data_list)} 条数据")
            
            if data_list:
                df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                print(f"最新数据: {df.iloc[-1]}")
            else:
                print("没有获取到数据")
        else:
            print("获取数据失败")
        
        bs.logout()
        print("登出成功！")
    else:
        print("登录失败！")
except Exception as e:
    print(f"发生异常: {e}")
    import traceback
    traceback.print_exc()

print("测试完成！")
