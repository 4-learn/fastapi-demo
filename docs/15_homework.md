
## **情境：AI 系統的「第一個入口」**

你正在設計一個 AI 系統的第一個 API。

這個 API 的責任不是「做出 AI 結果」，而是：

- 接收 Camera Event（違規事件）
- 確保資料合理
- 讓資料「可以被 AI 使用」

未來這個 API 可能會接：

- Ch-05 YOLO（影像辨識）
- Ch-06 LLM（摘要 / 解釋 / 法規查詢）
- Data Pipeline（長期分析）

但現在 **你不需要真的接 AI**。

你的目標只有一個：

👉 **這個 API，AI 看得懂，也用得上。**

---

## **延續 Ch-03：從分析到 API**

Ch-03 我們用 Pandas 分析了 Camera Event：

```python
raw_events = [
    {"image": "IMG_001.jpg", "time": "2024-12-31 08:30:00",
     "type": "未戴安全帽", "location": "A工地"},
    ...
]
analyzer = ViolationAnalyzer()
analyzer.load_events(raw_events)
```

Ch-04 的問題是：**這些事件從哪來？**

答案：透過 API 接收。

---

## **最終實作目標**

你的 API 至少要做到：

| 要求 | 說明 |
|------|------|
| ✅ 清楚的事件語意 | 違規類型要有明確定義 |
| ✅ 明確的 Schema | 使用 Pydantic |
| ✅ 有基本 Validation | 必填欄位、格式檢查 |
| ✅ Response 是 AI-ready | 標準化的結構化資料 |
| ❌ 不需要真的跑模型 | |
| ❌ 不需要真的存 DB | In-memory 即可 |

---

## **功能需求**

### 你要實作的 API：

```
POST /events/violation
```

### 事件語意

> 一個「違規事件」來自工地監控攝影機

包含：

* 影像檔名
* 發生時間
* 違規類型（未戴安全帽、未穿反光背心...）
* 工地位置
* 辨識信心度

---

### Request Schema

```json
{
  "image_id": "IMG_001.jpg",
  "timestamp": "2024-12-31T08:30:00",
  "violation_type": "未戴安全帽",
  "location": "A工地",
  "confidence": 0.95
}
```

---

### Validation 要求

| 欄位 | 規則 |
|------|------|
| `image_id` | 必填，不能為空 |
| `timestamp` | 必填，合法 ISO-8601 時間 |
| `violation_type` | 必填，不能為空 |
| `location` | 選填 |
| `confidence` | 選填，0.0-1.0 |

---

### Response 要求

Response **不是 echo 原始資料**，而是：

```json
{
  "event_id": "7748ab99",
  "received_at": "2026-01-10T13:10:59.182278",
  "event_type": "no_helmet",
  "normalized_event": {
    "event_type": "no_helmet",
    "event_type_raw": "未戴安全帽",
    "image_id": "IMG_001.jpg",
    "occurred_at": "2024-12-31T08:30:00",
    "location": "A工地",
    "confidence": 0.95,
    "description": ""
  },
  "ai_ready": true
}
```

📌 重點：
- `event_type` 是標準化代碼（AI 友善）
- `event_type_raw` 保留原始中文
- `ai_ready: true` 表示已可供 AI 使用

---

## **違規類型對照表**

| 中文 | 標準化代碼 |
|------|-----------|
| 未戴安全帽 | `no_helmet` |
| 未穿反光背心 | `no_vest` |
| 未穿安全鞋 | `no_safety_shoes` |
| 未戴護目鏡 | `no_goggles` |
| 施工架未固定 | `unsafe_scaffolding` |
| 未繫安全帶 | `no_safety_harness` |
| 其他違規 | `other` |

---

## **設計限制**

| ❌ 不要 | ✅ 要 |
|--------|-------|
| 直接回傳 request 原樣 | 做資料標準化 |
| 寫成 CRUD | 專注於 Ingest |
| 在 API 裡做重計算 | 保持簡單 |

---

## **進階功能（選做）**

1. `GET /events` - 列出已接收的事件
2. `GET /events/stats` - 整合 Ch-03 的統計分析
3. `POST /events/violation/batch` - 批次接收

---

## **交付內容**

1. `api/schemas.py` - Pydantic models
2. `api/main.py` - FastAPI app
3. 一個 `POST /events/violation` endpoint
4. 能在 `/docs` 中測試
5. 能解釋：
   * 為什麼這樣設計 event
   * 為什麼 AI 會吃得下這個資料

---

## **測試方式**

啟動 API：
```bash
uvicorn api.main:app --reload
```

測試接收事件：
```bash
curl -X POST http://localhost:8000/events/violation \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "IMG_001.jpg",
    "timestamp": "2024-12-31T08:30:00",
    "violation_type": "未戴安全帽",
    "location": "A工地",
    "confidence": 0.95
  }'
```

查看統計（整合 Ch-03）：
```bash
curl http://localhost:8000/events/stats
```

Swagger UI：
```
http://localhost:8000/docs
```

---

## **解答**

解答請參考：[GitHub - ch-04-fastapi-ingestion](https://github.com/4-learn/event-driven-alert-system/tree/ch-04-fastapi-ingestion)

主要檔案：
- `api/schemas.py` - Request/Response Schema 定義
- `api/main.py` - FastAPI 應用程式
- `api/__init__.py` - 模組匯出

---

原始課綱：[打造一個「AI-ready API」](https://hackmd.io/@yillkid/SkgEInkrbg)
