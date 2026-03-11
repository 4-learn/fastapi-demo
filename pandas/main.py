from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import pandas as pd


# --------------------------------------------------
# Event Store（用 CSV 模擬）
# --------------------------------------------------
DATA_PATH = Path(__file__).parent / "events.csv"


# --------------------------------------------------
# Schema
# --------------------------------------------------
class UserSummary(BaseModel):
    user_id: int
    total_events: int
    total_amount: float
    avg_confidence: float | None
    note: str | None = None


# --------------------------------------------------
# Service：用 Pandas 整理歷史事件
# --------------------------------------------------
def get_user_summary(user_id: int) -> UserSummary:
    """
    從 Event Store 讀取資料，篩選指定使用者，回傳摘要。

    Pandas 在這裡的角色：整理歷史，不是即時判斷。
    """
    df = pd.read_csv(DATA_PATH)
    user_df = df[df["user_id"] == user_id]

    if user_df.empty:
        return UserSummary(
            user_id=user_id,
            total_events=0,
            total_amount=0,
            avg_confidence=None,
            note="no historical events",
        )

    return UserSummary(
        user_id=user_id,
        total_events=len(user_df),
        total_amount=float(user_df["amount"].sum()),
        avg_confidence=round(float(user_df["confidence"].mean()), 2),
    )


def get_event_breakdown(user_id: int) -> dict:
    """
    按 event_type 分組統計——示範 Pandas groupby。
    """
    df = pd.read_csv(DATA_PATH)
    user_df = df[df["user_id"] == user_id]

    if user_df.empty:
        return {"user_id": user_id, "breakdown": {}}

    grouped = user_df.groupby("event_type").agg(
        count=("event_id", "count"),
        total_amount=("amount", "sum"),
        avg_confidence=("confidence", "mean"),
    )

    return {
        "user_id": user_id,
        "breakdown": {
            event_type: row.to_dict()
            for event_type, row in grouped.iterrows()
        },
    }


# --------------------------------------------------
# App
# --------------------------------------------------
app = FastAPI(title="Event DataFrame Demo")


@app.get("/users/{user_id}/summary")
def user_summary(user_id: int):
    """查詢使用者歷史行為摘要"""
    return get_user_summary(user_id)


@app.get("/users/{user_id}/breakdown")
def user_breakdown(user_id: int):
    """按事件類型分組統計"""
    return get_event_breakdown(user_id)
