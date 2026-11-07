# HTTP Request 的三層結構

> **定位**：一個 request 的資料不是全部塞在同一個地方——Path、Query、Body 各有各的責任。

## 學習目標

完成本節後，你應該能夠：
- 區分 Path、Query、Body 三者的責任
- 判斷資料該放在哪裡
- 用 FastAPI 寫出包含三層的 API

## 範例程式碼

- [demo](https://github.com/4-learn/fastapi-demo/tree/main/http)

---

# Part 1：Path — 資源的身份證

## 情境

你走進一間飲料店，跟店員說「我要看那杯飲料」——**哪一杯**就是 Path。

沒有說哪一杯，店員根本不知道你在講什麼。Path 就是資源的身份證，少了它，事件不成立。

## 講解

```python
@app.get("/drinks/{drink_id}")
def get_drink(drink_id: str):
    """drink_id 就是這杯飲料的身份證"""
    drink = DRINKS[drink_id]
    return {"drink_id": drink_id, "name": drink["name"], "price": drink["price"]}
```

**判斷標準**：拿掉這個參數，API 還有意義嗎？沒有 → 放 Path。

### Demo

```bash
# 啟動 server
cd fastapi-demo/http/part1-path
uvicorn main:app --reload

# 測試
curl http://localhost:8000/drinks
curl http://localhost:8000/drinks/bubble-tea
curl http://localhost:8000/drinks/green-tea
```

## Workshop

### 題目

用**學生餐廳菜單**做一個 API：

1. `GET /menu` → 列出所有餐點
2. `GET /menu/{item_id}` → 取得指定餐點
3. `GET /menu/{item_id}/reviews/{review_id}` → 取得某餐點的某則評價（多層 Path）

### 提示
```python=
@app.get("/menu/{item_id}/reviews/{review_id}")
def get_review(item_id: str, review_id: int):
    """多層 Path：取得某餐點的某則評價"""
    return {
        "item_id": item_id,
        "review_id": review_id,
        "comment": "好好吃！",
        "rating": 5,
    }
```

### 預期輸出

```json
// GET /menu/fried-rice
{"item_id": "fried-rice", "name": "炒飯", "price": 80}

// GET /menu/fried-rice/reviews/1
{"item_id": "fried-rice", "review_id": 1, "comment": "好好吃！", "rating": 5}
```

### 解答

- [解答](https://github.com/4-learn/fastapi-workspace/tree/main/http/part1-path)

---

# Part 2：Query — 篩選與選項

## 情境

你跟店員說「我要看菜單，只看**茶類**、**50 元以下**的」——這些篩選條件就是 Query。

拿掉條件？菜單還是菜單，只是沒篩選而已。

## 講解

```python
@app.get("/drinks")
def list_drinks(category: str = None, max_price: int = None):
    """category 和 max_price 都是篩選條件，拿掉也不影響事件本身"""
    results = {}
    for drink_id, info in DRINKS.items():
        if category and info["category"] != category:
            continue
        if max_price and info["price"] > max_price:
            continue
        results[drink_id] = info
    return results
```

**判斷標準**：拿掉這個參數，API 還能用嗎？可以 → 放 Query。

FastAPI 規則：有預設值 + 不在 URL path 裡 → 自動變 Query。

### Demo
- -G 是 --get 的縮寫
- --data-urlencode 為了中文編碼

```bash
# 啟動 server
cd fastapi-demo/http/part2-query
uvicorn main:app --reload

# 測試
curl http://localhost:8000/drinks
curl -G "http://localhost:8000/drinks" --data-urlencode "category=茶"
curl "http://localhost:8000/drinks?max_price=40"
curl -G "http://localhost:8000/drinks" --data-urlencode "category=茶" --data-urlencode "max_price=40"
curl "http://localhost:8000/drinks/bubble-tea?show_price=false"
```

## Workshop

### 題目

延續學生餐廳，加入 Query 篩選：

1. `GET /menu?category=飯類&max_price=75&spicy_only=true` → 篩選餐點
2. `GET /menu/{item_id}?lang=en` → 用英文顯示餐點名稱

### 預期輸出

```json
// GET /menu?category=炸物
{"chicken-cutlet": {"name": "雞排", "price": 60, "category": "炸物", "spicy": true}}

// GET /menu/fried-rice?lang=en
{"item_id": "fried-rice", "name": "Fried Rice", "price": 80}
```

### 解答

- [解答](https://github.com/4-learn/fastapi-workspace/tree/main/http/part2-query)

---

# Part 3：Body — 寄送資料包裹

## 情境

你決定點餐了：「珍珠奶茶、大杯、少冰、半糖、兩杯」——這些完整的訂單資料就是 Body。

這不是在「看」東西，而是在「送」一包資料給店家處理。

## 講解

```python
@app.post("/orders")
def create_order(order: dict = Body(...)):
    """
    完整訂單放 Body：
    {"drink_id": "bubble-tea", "size": "大杯", "ice": "少冰", "sugar": "半糖", "quantity": 2}
    """
    order_id = len(orders) + 1
    orders.append({"order_id": order_id, "detail": order})
    return {"message": "點餐成功", "order_id": order_id, "detail": order}
```

**三層一起用：**

```python
@app.post("/drinks/{drink_id}/customize")
def customize_drink(
    drink_id: str,           # Path：哪杯飲料
    debug: bool = False,     # Query：要不要除錯資訊
    options: dict = Body(...)  # Body：客製化內容
):
    ...
```

| 位置 | 責任 | 判斷標準 |
|------|------|----------|
| Path | 身份證 | 拿掉就不知道在講誰 |
| Query | 篩選 / 選項 | 拿掉還是能用 |
| Body | 資料包裹 | 要送一包資料給 server |

### Demo

```bash
# 啟動 server
cd fastapi-demo/http/part3-body
uvicorn main:app --reload

# 點餐
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"drink_id": "bubble-tea", "size": "大杯", "ice": "少冰", "quantity": 2}'

# 三層一起用
curl -X POST "http://localhost:8000/drinks/bubble-tea/customize?debug=true" \
  -H "Content-Type: application/json" \
  -d '{"extra": "加布丁", "sugar": "無糖"}'
```

## Workshop

### 題目

延續學生餐廳，加入 Body：

1. `POST /orders` → 送出訂單（Body 包含 item_id, quantity, note）
2. `POST /menu/{item_id}/customize?preview=true` → 三層一起用（Path + Query + Body）

### 預期輸出

```json
// POST /orders  body: {"item_id": "fried-rice", "quantity": 2, "note": "不要蔥"}
{"message": "訂餐成功", "order_id": 1, "total": 160}

// POST /menu/fried-rice/customize?preview=true  body: {"extra": "加蛋", "spicy_level": 3}
{"item": "炒飯", "customization": {"extra": "加蛋", "spicy_level": 3}, "is_preview": true}
```

### 解答

- [解答](https://github.com/4-learn/fastapi-workspace/tree/main/http/part3-body)

---

原始課綱：[Request / Response 的真實結構](https://hackmd.io/@yillkid/rJzY2g-Nbe)
