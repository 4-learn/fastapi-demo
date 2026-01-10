# Async vs Sync Blocking Demo

展示 FastAPI 中 `time.sleep()` 與 `await asyncio.sleep()` 的阻塞差異。

## 結構

```
async-demo/
├── main.py      # FastAPI 應用
├── tasks.py     # 無窮迴圈任務
├── test.sh      # 測試腳本
└── README.md
```

## 核心概念

| API | 實作 | 結果 |
|-----|------|------|
| `/sync` | `async def` + `time.sleep()` | 阻塞 event loop |
| `/async` | `async def` + `await asyncio.sleep()` | 不阻塞 |

## 關鍵程式碼

```python
# tasks.py
def sync_infinite_loop():
    while True:
        time.sleep(1)  # 阻塞！不會讓出控制權

async def async_infinite_loop():
    while True:
        await asyncio.sleep(1)  # 讓出控制權給 event loop
```

```python
# main.py
@app.get("/sync")
async def sync_api():
    sync_infinite_loop()  # 阻塞整個 server

@app.get("/async")
async def async_api():
    await async_infinite_loop()  # 其他請求仍可處理
```

## 測試

```bash
# 啟動 server
uvicorn main:app --port 8005

# 另一個終端執行測試
./test.sh
```

## 預期結果

```
=== 測試 /sync (會阻塞) ===
嘗試 ping...
TIMEOUT - 被阻塞了！

=== 測試 /async (不會阻塞) ===
嘗試 ping...
{"message":"pong"} <- 成功回應！
```

## 重點

- 在 `async def` 中使用 `time.sleep()` 會阻塞整個 event loop
- 使用 `await asyncio.sleep()` 會讓出控制權，讓其他請求可以被處理
- FastAPI 的 `def`（非 async）函數會自動在線程池執行，不會阻塞 event loop
