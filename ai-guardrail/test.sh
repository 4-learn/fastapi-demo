#!/usr/bin/env bash
# 先在另一個終端機執行 uvicorn main:app --reload
set -eu
URL=${BASE_URL:-http://localhost:8000}
for confidence in 0.95 0.62 0.42; do
  printf '\n== overheat confidence=%s\n' "$confidence"
  curl -fsS "$URL/evaluate" -H 'Content-Type: application/json' \
    -d "{\"event_id\":\"sensor-01\",\"prediction\":{\"label\":\"overheat\",\"confidence\":$confidence}}"
  printf '\n'
done
printf '\n== normal confidence=0.99\n'
curl -fsS "$URL/evaluate" -H 'Content-Type: application/json' \
  -d '{"event_id":"sensor-02","prediction":{"label":"normal","confidence":0.99}}'
printf '\n\n== thresholds\n'
curl -fsS "$URL/thresholds"
printf '\n'
