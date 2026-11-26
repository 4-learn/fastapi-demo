#!/bin/bash
# 先在另一個終端機啟動 server：uvicorn main:app --reload
# 再執行：bash test.sh

URL=http://localhost:8000
JSON="Content-Type: application/json"

echo "== 1. 推論：aisle_01 → high_risk → auto_flag"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/risk/evaluate \
  -H "$JSON" -d '{"location": "aisle_01"}'

echo "== 2. 推論：aisle_02 → medium_risk → require_review"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/risk/evaluate \
  -H "$JSON" -d '{"location": "aisle_02"}'

echo "== 3. 推論：aisle_03 → low_risk → none"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/risk/evaluate \
  -H "$JSON" -d '{"location": "aisle_03"}'

echo "== 4. 推論：aisle_99（沒有歷史）→ low_risk → none"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/risk/evaluate \
  -H "$JSON" -d '{"location": "aisle_99"}'

echo "== 5. 摘要：不開 LLM → narrative 是 null"
curl -s -w "\nHTTP %{http_code}\n\n" $URL/locations/aisle_02/summary

echo "== 6. 摘要：?llm=true → 多了 narrative"
curl -s -w "\nHTTP %{http_code}\n\n" "$URL/locations/aisle_02/summary?llm=true"

echo "== 7. 摘要：沒有歷史 → 不呼叫 LLM"
curl -s -w "\nHTTP %{http_code}\n\n" "$URL/locations/aisle_99/summary?llm=true"

echo "== 8. 任務觸發 → pending（task_id、created_at 每次不同）"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/tasks/review \
  -H "$JSON" -d '{"location": "aisle_02", "reason": "medium_risk"}'

echo "== 9. 任務觸發少了 reason → 422"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST $URL/tasks/review \
  -H "$JSON" -d '{"location": "aisle_02"}'
