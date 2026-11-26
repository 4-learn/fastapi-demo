#!/usr/bin/env bash
# 另一個終端機先啟動 uvicorn main:app --reload，再 bash test.sh。
# 顯示回應供對照，不會啟動 server；第 8 步會新增一筆記憶體任務。
set -eu
URL=${BASE_URL:-http://localhost:8000}
show() { curl -sS --connect-timeout 5 --max-time 15 -w '\nHTTP %{http_code}\n\n' "$@"; }
for sensor in sensor_01 sensor_02 sensor_03 sensor_99; do
  echo "== 推論：$sensor"
  show "$URL/risk/evaluate" -H 'Content-Type: application/json' -d "{\"sensor_id\":\"$sensor\"}"
done
echo '== 5. 摘要：只回統計'
show "$URL/sensors/sensor_02/summary"
echo '== 6. 摘要：加上模擬 LLM 敘述'
show "$URL/sensors/sensor_02/summary?llm=true"
echo '== 7. 沒有歷史：不呼叫模擬模型'
show "$URL/sensors/sensor_99/summary?llm=true"
echo '== 8. 建立記憶體巡檢任務（不會執行）'
show "$URL/tasks/review" -H 'Content-Type: application/json' -d '{"sensor_id":"sensor_02","reason":"請確認機房散熱狀況"}'
echo '== 9. 少了 reason：422'
show "$URL/tasks/review" -H 'Content-Type: application/json' -d '{"sensor_id":"sensor_02"}'
