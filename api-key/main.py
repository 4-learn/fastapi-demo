"""
API Key 保護：Header 驗證與 401 / 403

執行：uvicorn main:app --reload
"""
import os

from fastapi import Depends, FastAPI, Header, HTTPException

# 正式環境一定要用環境變數設定，不要把真的 key 寫進程式碼
API_KEY = os.getenv("API_KEY", "dev-secret")

app = FastAPI(title="API Key Demo")

events = []


# --------------------------------------------------
# 檢查 Header 裡的 X-API-Key
# --------------------------------------------------
def verify_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="缺少 API Key")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="API Key 錯誤")


# --------------------------------------------------
# 不需要 key：誰都可以確認服務還活著
# --------------------------------------------------
@app.get("/ping")
def ping():
    return {"status": "pong"}


# --------------------------------------------------
# 需要 key：寫入事件
# --------------------------------------------------
@app.post("/events/{event_type}", dependencies=[Depends(verify_api_key)])
def create_event(event_type: str, payload: dict):
    events.append({"event_type": event_type, "payload": payload})
    return {"status": "accepted", "count": len(events)}


@app.get("/events")
def list_events():
    return events
