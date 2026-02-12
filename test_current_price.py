#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, r'D:\trae\备份悟空52220')

from strategy.data_provider import DataProvider

def test_get_current_price():
    """测试获取当前价格"""
    symbol = "002371"
    
    print("=" * 60)
    print(f"测试获取股票 {symbol} 的当前价格")
    print("=" * 60)
    
    price = DataProvider.get_current_price(symbol)
    
    print(f"当前价格: {price}")
    print("=" * 60)

if __name__ == "__main__":
    test_get_current_price()
