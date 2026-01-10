curl -X POST "http://127.0.0.1:8000/events/login?debug=true" \
    -H "Content-Type: application/json" \
    -d '{"user_id": 1, "timestamp": "2026-01-10T12:00:00", "payload": {"ip": "127.0.0.1"}}'
