from app import app
with app.test_request_context('/api/plan/buy'):
    from app import get_buy_strategy
    result = get_buy_strategy().get_json()
    suggestions = result.get('suggestions', [])
    print(f'买入建议数量: {len(suggestions)}')
    for s in suggestions:
        print(f"  {s['symbol']} {s['name']} - {s['reason']}")