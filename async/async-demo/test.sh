#!/bin/bash

PORT=8005

# 測試 sync（會阻塞）
echo "=== 測試 /sync (會阻塞) ==="
curl -s http://localhost:$PORT/sync &
sleep 2
echo "嘗試 ping..."
timeout 3 curl -s http://localhost:$PORT/ping || echo "TIMEOUT - 被阻塞了！"

# 重啟 server
echo ""
echo "重啟 server..."
pkill -f "uvicorn main:app.*$PORT" 2>/dev/null
sleep 1
uvicorn main:app --port $PORT &
sleep 2

# 測試 async（不會阻塞）
echo ""
echo "=== 測試 /async (不會阻塞) ==="
curl -s http://localhost:$PORT/async &
sleep 2
echo "嘗試 ping..."
timeout 3 curl -s http://localhost:$PORT/ping && echo " <- 成功回應！"

# 清理
pkill -f "uvicorn main:app.*$PORT" 2>/dev/null
