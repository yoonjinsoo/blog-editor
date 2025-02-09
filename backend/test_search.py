import requests

response = requests.post('http://localhost:5000/search', data={'keyword': '쿠팡 퀵플렉스'})
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
