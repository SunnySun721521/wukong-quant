#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_market_status():
    """测试获取市场状态"""
    url = "http://127.0.0.1:5006/api/plan/market-status"
    
    print("=" * 60)
    print("测试获取市场状态")
    print("=" * 60)
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        print(f"市场状态: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result.get('status')
    except Exception as e:
        print(f"❌ 获取市场状态失败: {e}")
        return None

def test_position():
    """测试获取持仓数据"""
    url = "http://127.0.0.1:5006/api/plan/position"
    
    print("=" * 60)
    print("测试获取持仓数据")
    print("=" * 60)
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        print(f"持仓数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except Exception as e:
        print(f"❌ 获取持仓数据失败: {e}")
        return None

def test_available_cash():
    """测试获取可用资金"""
    url = "http://127.0.0.1:5006/api/config/available_cash"
    
    print("=" * 60)
    print("测试获取可用资金")
    print("=" * 60)
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        print(f"可用资金: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result.get('available_cash')
    except Exception as e:
        print(f"❌ 获取可用资金失败: {e}")
        return None

def test_buy_api():
    """测试买入API"""
    
    # 先获取各项数据
    market_status = test_market_status()
    print()
    position_data = test_position()
    print()
    available_cash = test_available_cash()
    print()
    
    # 计算总资产
    positions = position_data.get('positions', [])
    position_value = position_data.get('position_value', 0)
    total_assets = available_cash + position_value
    
    print("=" * 60)
    print("仓位分析")
    print("=" * 60)
    print(f"可用资金: {available_cash}")
    print(f"持仓市值: {position_value}")
    print(f"总资产: {total_assets}")
    print(f"市场状态: {market_status}")
    print(f"当前持仓数量: {len(positions)}")
    
    # 计算目标仓位
    is_bull_market = market_status == 'bull'
    target_position_pct = 0.8 if is_bull_market else 0.3
    target_position_value = total_assets * target_position_pct
    
    print(f"目标仓位: {target_position_pct * 100}%")
    print(f"目标持仓市值: {target_position_value}")
    print(f"当前持仓市值: {position_value}")
    
    # 检查是否可以买入
    if position_value >= target_position_value:
        print(f"❌ 当前仓位已达到目标仓位{target_position_pct * 100}%，无法继续买入")
        return
    
    # 计算可用买入金额
    available_buy_amount = min(available_cash, target_position_value - position_value)
    print(f"可用买入金额: {available_buy_amount}")
    
    # 测试数据
    test_data = {
        "symbol": "002371",
        "name": "北方华创",
        "quantity": 100,
        "cost_price": 200.0
    }
    
    url = "http://127.0.0.1:5006/api/plan/position"
    
    print()
    print("=" * 60)
    print("测试买入API")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print()
        
        try:
            result = response.json()
            print(f"响应内容:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except:
            print(f"响应内容（非JSON）:")
            print(response.text)
        
        print()
        
        if response.status_code == 201:
            print("✅ 买入成功！")
        else:
            print(f"❌ 买入失败，状态码: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请检查服务器是否运行")
    except Exception as e:
        print(f"❌ 发生异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    test_buy_api()
