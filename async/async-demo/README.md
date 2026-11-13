# Async vs Sync Blocking Demo

展示 FastAPI 中 `time.sleep()` 與 `await asyncio.sleep()` 的阻塞差異。

## 結構

```
async-demo/
├── main.py      # FastAPI 應用
├── server.sh    # 啟動 server（port 8005）
├── test.sh      # 測試腳本
└── README.md
```

## 核心概念

| API | 實作 | 結果 |
|-----|------|------|
| `/sync` | `async def` + `time.sleep(5)` | 阻塞 event loop，`/ping` 也要等 |
| `/async` | `async def` + `await asyncio.sleep(5)` | 不阻塞，`/ping` 馬上回 |

## 測試

```bash
# 終端機 A：啟動 server
bash server.sh

# 終端機 B：執行測試
bash test.sh
```

`test.sh` 測完 `/sync` 之後，會自己重啟 server，再測 `/async`。

## 預期結果（節錄）

```
=== 測試 /sync (會阻塞) ===
嘗試 ping...
TIMEOUT - 被阻塞了！

=== 測試 /async (不會阻塞) ===
嘗試 ping...
{"status":"pong"} <- 成功回應！
```

中間還會穿插 `{"status":"done"}` 和 server 的 `INFO:` 記錄，是背景請求跑完時印出來的，可以忽略。

## 重點

- 在 `async def` 中使用 `time.sleep()` 會阻塞整個 event loop
- 使用 `await asyncio.sleep()` 會讓出控制權，讓其他請求可以被處理
- FastAPI 的 `def`（非 async）函數會自動在線程池執行，不會阻塞 event loop
