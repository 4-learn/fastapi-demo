# Workshop：設計一個事件型 API

> **承接**：FastAPI 基礎、HTTP 結構、Schema、Validation
> **目標**：把前面學的東西串起來，設計一個正式的事件入口

---

## 情境

你加入了一間做 AI 行為分析的新創公司。系統需要接收各種使用者行為事件（點擊、交易、登入），然後送進下游的 AI pipeline 分析。

目前的狀況：前端直接把 JSON 丟過來，格式每次都不一樣，AI 模型常常收到壞資料然後炸掉。

你的任務是設計一個**統一的事件入口 API**，確保：
1. 每個 request 代表一個事件
2. 資料結構有 Schema 合約
3. 語意有 Validation 檢查
4. Path / Query / Body 各司其職

---

## 你的任務

### API 設計

```
POST /events/{event_type}?debug=false
```

- **Path**: `event_type`（必要）— click、transaction、login
- **Query**: `debug`（選填，預設 false）— 是否回傳額外除錯資訊
- **Body**: 事件內容

### Schema 定義

```python
class EventPayload(BaseModel):
    user_id: int = Field(gt=0)
    timestamp: str = Field(min_length=1)
    payload: dict
```

### 需要實作

1. 定義 `EventPayload` Schema（含 Validation）
2. 建立 `POST /events/{event_type}` endpoint
3. 處理 Path（event_type）、Query（debug）、Body（EventPayload）
4. debug=true 時回傳 payload 細節，debug=false 時不回傳

---

## 預期輸出

正常事件（debug=false）：

```json
{
  "status": "accepted",
  "event_type": "click",
  "user_id": 123,
  "timestamp": "2025-01-10T10:00:00"
}
```

正常事件（debug=true）：

```json
{
  "status": "accepted",
  "event_type": "click",
  "user_id": 123,
  "timestamp": "2025-01-10T10:00:00",
  "payload": {"page": "/home", "button": "signup"}
}
```

Schema 錯誤（user_id 缺失）：

```json
{
  "detail": [
    {
      "loc": ["body", "user_id"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

Validation 錯誤（user_id = -1）：

```json
{
  "detail": [
    {
      "loc": ["body", "user_id"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

---

## 提示

1. 先定義 Schema，再寫 endpoint
2. 用 Swagger 測試每一種情境
3. 想清楚 event_type 為什麼放 Path 不放 Body

---

## 解答

- [解答](https://github.com/4-learn/fastapi-workshop/tree/main/event-api)

---

原始課綱：[設計一個「事件型 API」](https://hackmd.io/@yillkid/Hkq5KeLEWe)
