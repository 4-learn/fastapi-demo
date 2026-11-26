#!/usr/bin/env bash
# 終端機 A：在 pandas 目錄啟動 uvicorn main:app --reload
# 終端機 B：bash test.sh
# 只查詢，不修改 events.csv，也不會啟動或停止 server。
set -eu
URL=${BASE_URL:-http://localhost:8000}

show() {
  curl --silent --show-error --fail --connect-timeout 5 --max-time 15 \
    --write-out '\nHTTP %{http_code}\n\n' "$@"
}

printf '== 1. 使用者 123 的摘要（4 筆、金額 2500、平均信心值 0.84）\n'
show "$URL/users/123/summary"

printf '== 2. 使用者 999 沒有歷史紀錄（0 筆，不是 404）\n'
show "$URL/users/999/summary"

printf '== 3. 使用者 123 的分類明細（login 1 筆、transaction 3 筆）\n'
show "$URL/users/123/breakdown"

printf '== 4. 使用者 999 的分類明細（空的 breakdown）\n'
show "$URL/users/999/breakdown"
