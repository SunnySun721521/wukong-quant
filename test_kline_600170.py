#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_kline_api():
    """测试获取上海建工的K线数据"""
    
    symbol = "600170"
    url = f"http://127.0.0.1:5006/api/stocks/kline?symbol={symbol}&start_date=2026-01-01"
    
    print("=" * 60)
    print("测试获取上海建工（600170）的K线数据")
    print("=" * 60)
    print(f"URL: {url}")
    print()
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print()
        
        try:
            result = response.json()
            print(f"响应内容:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            if 'kline' in result and result['kline']:
                print(f"\nK线数据条数: {len(result['kline'])}")
                if result['kline']:
                    print(f"最新价格: {result['kline'][-1]['close']}")
        except:
            print(f"响应内容（非JSON）:")
            print(response.text)
        
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
    test_kline_api()
