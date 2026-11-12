"""
Pydantic：Schema = 合約

執行：uvicorn main:app --reload
測試：打開 http://localhost:8000/docs
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class TransactionEvent(BaseModel):
    user_id: int
    amount: float
    currency: str


@app.post("/transactions")
def receive_transaction(event: TransactionEvent):
    return {"status": "accepted", "event": event.model_dump()}
