"""
資料驗證：Schema 擋結構，Validation 擋語意

執行：uvicorn main:app --reload
測試：打開 http://localhost:8000/docs
"""
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class TransactionEvent(BaseModel):
    user_id: int = Field(gt=0)            # 必須大於 0
    amount: float = Field(gt=0)           # 金額必須正數
    currency: str = Field(min_length=3, max_length=3)  # 貨幣代碼三碼
    note: Optional[str] = None            # 可以不給


@app.post("/transactions")
def receive_transaction(event: TransactionEvent):
    return {"status": "accepted", "event": event.model_dump()}
