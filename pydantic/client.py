import requests

r = requests.post(
    "http://localhost:8000/transactions",
    json={"user_id": 123, "amount": 500.0, "currency": "TWD"},
)
print(r.status_code)
print(r.json())
