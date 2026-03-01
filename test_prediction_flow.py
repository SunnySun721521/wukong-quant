#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from strategy.data_provider import DataProvider
from strategy.stock_predictor import StockPredictor, MultiStockPredictor
from datetime import datetime

def test_prediction_flow():
    symbol = "600519"
    start_date = "20230101"
    end_date = datetime.now().strftime("%Y%m%d")
    predict_days = 5
    model_type = "linear_regression"
    
    print(f"Testing prediction flow for symbol: {symbol}")
    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")
    print(f"Predict days: {predict_days}")
    print(f"Model type: {model_type}")
    
    # 1. 获取K线数据
    print("\n1. 获取K线数据...")
    df = DataProvider.get_kline_data(symbol, start_date, end_date)
    print(f"DataFrame type: {type(df)}")
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {df.columns.tolist()}")
    print(f"DataFrame columns dtypes: {df.dtypes}")
    
    if df is not None and not df.empty:
        # 2. 创建MultiStockPredictor
        print("\n2. 创建MultiStockPredictor...")
        multi_predictor = MultiStockPredictor(model_type=model_type)
        
        # 3. 调用batch_predict方法
        print("\n3. 调用batch_predict方法...")
        stock_data_dict = {symbol: df}
        try:
            results = multi_predictor.batch_predict(stock_data_dict, predict_days)
            print(f"Prediction results: {results}")
            print("预测流程成功!")
        except Exception as e:
            print(f"预测流程失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("获取K线数据失败")

if __name__ == "__main__":
    test_prediction_flow()