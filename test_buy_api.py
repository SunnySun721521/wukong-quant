import requests
import json

response = requests.get('http://127.0.0.1:5006/api/plan/buy')
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
