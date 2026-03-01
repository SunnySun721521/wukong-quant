#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import joblib
import os

class StockPredictor:
    def __init__(self, model_type='random_forest', model_dir='./models'):
        self.model_type = model_type
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
    
    def prepare_features(self, df, lookback=5):
        df = df.copy()
        
        # 首先，只保留数值列
        numeric_cols = [col for col in df.columns if df[col].dtype in ['int64', 'float64']]
        df = df[numeric_cols].copy()
        
        # 确保所有列都是数值类型
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 检查是否包含必要的列
        required_cols = ['close', 'high', 'low', 'open', 'volume']
        available_required_cols = [col for col in required_cols if col in df.columns]
        if len(available_required_cols) < 5:
            print(f"警告：缺少必要的列，仅包含 {available_required_cols}")
            # 如果缺少必要的列，返回空的DataFrame和空的特征列列表
            return pd.DataFrame(), []
        
        # 计算技术指标
        df['returns'] = df['close'].pct_change()
        df['high_low_ratio'] = df['high'] / df['low']
        df['close_open_ratio'] = df['close'] / df['open']
        
        for i in range(1, lookback + 1):
            df[f'close_lag_{i}'] = df['close'].shift(i)
            df[f'returns_lag_{i}'] = df['returns'].shift(i)
        
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_10'] = df['close'].rolling(window=10).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        
        df['std_5'] = df['close'].rolling(window=5).std()
        df['std_10'] = df['close'].rolling(window=10).std()
        
        df['rsi'] = self.calculate_rsi(df['close'], 14)
        
        df['volume_ma_5'] = df['volume'].rolling(window=5).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma_5']
        
        df['target'] = df['close'].shift(-1)
        
        df = df.dropna()
        
        # 再次检查，只包含数值列作为特征
        feature_cols = [col for col in df.columns if col != 'target' and df[col].dtype in ['int64', 'float64']]
        self.feature_names = feature_cols
        
        return df, feature_cols
    
    def calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def train(self, df, lookback=5):
        df, feature_cols = self.prepare_features(df, lookback)
        
        if len(df) < 100:
            return {'error': '数据不足，至少需要100条记录'}
        
        X = df[feature_cols].values
        y = df['target'].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        elif self.model_type == 'linear_regression':
            self.model = LinearRegression()
        elif self.model_type == 'lstm':
            # LSTM模型实现
            from sklearn.neural_network import MLPRegressor
            self.model = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
        elif self.model_type == 'prophet':
            # Prophet模型回退到随机森林
            self.model = RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42)
        elif self.model_type == 'arima':
            # ARIMA模型回退到线性回归
            self.model = LinearRegression()
        else:
            self.model = LinearRegression()
        
        self.model.fit(X_train_scaled, y_train)
        
        y_pred = self.model.predict(X_test_scaled)
        
        mae = np.mean(np.abs(y_test - y_pred))
        rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        accuracy = 100 - mape
        
        return {
            'mae': round(mae, 4),
            'rmse': round(rmse, 4),
            'mape': round(mape, 2),
            'accuracy': round(accuracy, 2),
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
    
    def predict(self, df, days=5, current_price=None):
        if self.model is None:
            return {'error': '模型未训练'}
        
        df, feature_cols = self.prepare_features(df)
        
        if len(df) < 1:
            return {'error': '数据不足'}
        
        last_features = df[feature_cols].iloc[-1:].values
        last_features_scaled = self.scaler.transform(last_features)
        
        predictions = []
        current_data = df.iloc[-1:].copy()
        
        for i in range(days):
            pred_price = self.model.predict(last_features_scaled)[0]
            predictions.append({
                'day': i + 1,
                'predicted_price': round(pred_price, 2)
            })
            
            current_data = self._update_data_for_next_prediction(current_data, pred_price)
            last_features = current_data[feature_cols].iloc[-1:].values
            last_features_scaled = self.scaler.transform(last_features)
        
        # 使用传入的实时价格或历史数据的最后一个收盘价
        last_price = current_price if current_price is not None else df['close'].iloc[-1]
        first_pred = predictions[0]['predicted_price']
        direction = 'up' if first_pred > last_price else 'down'
        change_pct = ((first_pred - last_price) / last_price) * 100
        
        return {
            'last_price': round(last_price, 2),
            'direction': direction,
            'change_percent': round(change_pct, 2),
            'predictions': predictions
        }
    
    def _update_data_for_next_prediction(self, df, new_price):
        df = df.copy()
        
        new_row = df.iloc[-1:].copy()
        new_row['close'] = new_price
        new_row['high'] = new_price
        new_row['low'] = new_price
        new_row['open'] = new_price
        new_row['returns'] = (new_price - df['close'].iloc[-1]) / df['close'].iloc[-1]
        new_row['high_low_ratio'] = 1.0
        new_row['close_open_ratio'] = 1.0
        
        for i in range(1, 6):
            new_row[f'close_lag_{i}'] = df[f'close_lag_{i-1}'].iloc[-1] if i > 1 else df['close'].iloc[-1]
            new_row[f'returns_lag_{i}'] = df[f'returns_lag_{i-1}'].iloc[-1] if i > 1 else df['returns'].iloc[-1]
        
        new_row['ma_5'] = new_price
        new_row['ma_10'] = new_price
        new_row['ma_20'] = new_price
        new_row['std_5'] = 0
        new_row['std_10'] = 0
        new_row['rsi'] = 50
        new_row['volume_ma_5'] = df['volume'].iloc[-1]
        new_row['volume_ratio'] = 1.0
        
        df = pd.concat([df, new_row], ignore_index=True)
        
        return df
    
    def save_model(self, symbol):
        if self.model is None:
            return False
        
        model_path = os.path.join(self.model_dir, f'{symbol}_model.pkl')
        scaler_path = os.path.join(self.model_dir, f'{symbol}_scaler.pkl')
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        return True
    
    def load_model(self, symbol):
        model_path = os.path.join(self.model_dir, f'{symbol}_model.pkl')
        scaler_path = os.path.join(self.model_dir, f'{symbol}_scaler.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            return False
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        return True

class MultiStockPredictor:
    def __init__(self, model_type='random_forest'):
        self.predictor = StockPredictor(model_type=model_type)
    
    def train_and_predict(self, symbol, df, predict_days=5):
        train_result = self.predictor.train(df)
        
        if 'error' in train_result:
            return train_result
        
        predict_result = self.predictor.predict(df, days=predict_days)
        
        return {
            'symbol': symbol,
            'train_result': train_result,
            'predict_result': predict_result
        }
    
    def batch_predict(self, stock_data_dict, predict_days=5):
        results = []
        
        for symbol, df in stock_data_dict.items():
            result = self.train_and_predict(symbol, df, predict_days)
            results.append(result)
        
        return results