#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_position_api():
    """测试持仓API"""
    
    url = "http://127.0.0.1:5006/api/plan/position"
    
    print("=" * 60)
    print("测试持仓API")
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
            
            if 'positions' in result and result['positions']:
                print(f"\n持仓数量: {len(result['positions'])}")
                print("\n持仓明细:")
                for pos in result['positions']:
                    position_amount = pos['quantity'] * pos['current_price']
                    print(f"  {pos['symbol']} {pos['name']}: 数量={pos['quantity']}, 现价={pos['current_price']}, 持仓金额={position_amount:.2f}")
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
    test_position_api()
