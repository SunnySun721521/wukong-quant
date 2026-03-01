import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from strategy.data_provider import DataProvider
    print("✓ DataProvider 导入成功")
    
    # 测试获取价格
    test_symbol = "600519"
    print(f"\n正在测试获取 {test_symbol} 的价格...")
    price = DataProvider.get_current_price(test_symbol)
    print(f"获取结果: {price}")
    
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
