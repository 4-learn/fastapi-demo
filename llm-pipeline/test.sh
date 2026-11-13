#!/bin/bash
# 先在另一個終端機啟動 server：uvicorn main:app --reload
# 再執行：bash test.sh

URL=http://localhost:8000
JSON="Content-Type: application/json"

echo "== 1. 推論：user 789 → high_risk → auto_flag"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/risk/evaluate \
  -H "$JSON" -d '{"user_id": 789}'

echo "== 2. 推論：user 123 → medium_risk → require_review"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/risk/evaluate \
  -H "$JSON" -d '{"user_id": 123}'

echo "== 3. 推論：user 456 → low_risk → none"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/risk/evaluate \
  -H "$JSON" -d '{"user_id": 456}'

echo "== 4. 推論：user 999（沒有歷史）→ low_risk → none"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/risk/evaluate \
  -H "$JSON" -d '{"user_id": 999}'

echo "== 5. 摘要：不開 LLM → narrative 是 null"
curl -s -w "\nHTTP %{http_code}\n\n" $URL/users/123/summary

echo "== 6. 摘要：?llm=true → 多了 narrative"
curl -s -w "\nHTTP %{http_code}\n\n" "$URL/users/123/summary?llm=true"

echo "== 7. 摘要：沒有歷史 → 不呼叫 LLM"
curl -s -w "\nHTTP %{http_code}\n\n" "$URL/users/999/summary?llm=true"

echo "== 8. 任務觸發 → pending（task_id、created_at 每次不同）"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/tasks/review \
  -H "$JSON" -d '{"user_id": 123, "reason": "medium_risk"}'

echo "== 9. 任務觸發少了 reason → 422"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/tasks/review \
  -H "$JSON" -d '{"user_id": 123}'
