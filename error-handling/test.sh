#!/bin/bash
# 先在另一個終端機啟動 server：uvicorn main:app --reload
# 再執行：bash test.sh

URL=http://localhost:8000/events
BODY='{"user_id": 123, "timestamp": "2025-01-10T12:00:00", "payload": {"amount": 500}}'

echo "== 1. 正常事件 → 200"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/click \
  -H "Content-Type: application/json" -d "$BODY"

echo "== 2. 不支援的 event_type → 400 EventRejected"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/unknown_action \
  -H "Content-Type: application/json" -d "$BODY"

echo "== 3. 使用者不存在 → 404 EventNotFound"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/click \
  -H "Content-Type: application/json" \
  -d '{"user_id": 9999, "timestamp": "2025-01-10T12:00:00", "payload": {}}'

echo "== 4. 缺欄位 → 422（覆寫後的格式）"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/click \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123, "payload": {}}'

echo "== 5. transaction 少了 amount → 500（系統的錯，沒有統一格式）"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/transaction \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123, "timestamp": "2025-01-10T12:00:00", "payload": {}}'
