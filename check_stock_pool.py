import sys
sys.path.append('d:\\trae\\备份悟空52216')

from strategy.stock_pool_manager import StockPoolManager

stock_pool_manager = StockPoolManager()

print("当前股票池:")
print("=" * 60)
for symbol in stock_pool_manager.current_pool:
    name = stock_pool_manager.get_stock_name(symbol)
    print(f"  {symbol} {name}")

print(f"\n当前股票池共 {len(stock_pool_manager.current_pool)} 只股票")

print(f"\n检查宁德时代(300750)是否在当前股票池中:")
if '300750' in stock_pool_manager.current_pool:
    print("  ✓ 宁德时代在当前股票池中")
else:
    print("  ✗ 宁德时代不在当前股票池中")
