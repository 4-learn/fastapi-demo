#!/bin/bash
# 先在另一個終端機啟動 server：uvicorn main:app --reload
# 再執行：bash test.sh

URL=http://localhost:8000

# 每收到一行，就在前面印出「從送出 request 到現在過了幾秒」
timed() {
  python3 -c '
import sys, time
start = time.time()
for line in sys.stdin:
    line = line.rstrip("\n")
    if line:
        print(f"{time.time() - start:4.1f}s  {line}", flush=True)
'
}

echo "== 1. 一般回應：等全部生完，才一次出現"
curl -s $URL/summary/123 | timed
echo

echo "== 2. 串流回應：每 0.5 秒出現一段"
curl -sN $URL/summary/123/stream | timed
echo

echo "== 3. 串流的 response header"
curl -sN -D - -o /dev/null $URL/summary/123/stream
echo

echo "== 4. 不存在的使用者（串流）：目前先回 200 再斷線，做完 Workshop 第 2 題會變成 404"
curl -s -i -N $URL/summary/999/stream
rc=$?
echo
echo "curl 結束代碼：$rc（0 = 正常結束，18 = 傳輸中斷）"
