from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import csv
import os
import sys
import time
import random
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# 导入DataProvider类和BacktestEngine类
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from strategy.data_provider import DataProvider
from strategy.backtest_engine import BacktestEngine
from strategy.stock_pool_manager import StockPoolManager

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

LOG_DIR = "../logs"
CACHE = {}
CACHE_EXPIRY = 300
CACHE_ACCESS_COUNT = {}

# 模拟数据
class MockStockPoolManager:
    def __init__(self, log_dir=None):
        # 默认股票池，只能通过股票池管理API修改
        self.default_pool = ['600519', '000858', '002371']
