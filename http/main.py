from fastapi import FastAPI, Body

app = FastAPI(
    title="Request / Response 真實結構（無 schema 版）",
    description="專注在 Path / Query / Body 的責任，而不是資料驗證",
)

# =========================
# 任務 1：Path = 事件身份
# =========================

@app.get("/items/{item_id}")
def get_item(item_id: int):
    """
    事件：取得某一個 item
    item_id 是事件對象
    """
    return {
        "event": "get_item",
        "item_id": item_id
    }


# =========================
# 任務 2：Query = 觀察條件
# =========================

@app.get("/items/{item_id}/detail")
def get_item_detail(item_id: int, verbose: bool = False):
    """
    事件：查看 item
    verbose 只是觀看方式
    """
    return {
        "event": "get_item_detail",
        "item_id": item_id,
        "verbose": verbose
    }


# =========================
# 任務 3：Body = 事件內容
# =========================

@app.post("/items/{item_id}/action")
def item_action(
    item_id: int,
    payload: dict = Body(...)
):
    """
    事件：對 item 做某個行為
    payload 是事件實際內容
    """
    return {
        "event": "item_action",
        "item_id": item_id,
        "payload": payload
    }

