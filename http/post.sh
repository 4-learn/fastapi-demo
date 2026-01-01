curl -X POST http://127.0.0.1:8000/items/10/action \
  -H "Content-Type: application/json" \
  -d '{
    "action": "buy",
    "quantity": 2
  }'
