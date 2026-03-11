from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import pandas as pd


# --------------------------------------------------
# Event Store（用 CSV 模擬）
# --------------------------------------------------
DATA_PATH = Path(__file__).parent / "events.csv"


# --------------------------------------------------
# Schema
# --------------------------------------------------
class RiskRequest(BaseModel):
    user_id: int


class RiskResult(BaseModel):
    user_id: int
    risk_level: str
    confidence: float
    action: str
    features: dict


class SummaryResult(BaseModel):
    user_id: int
    total_events: int
    total_amount: float
    avg_confidence: float | None
    narrative: str | None = None


class TaskRequest(BaseModel):
    user_id: int
    reason: str


class TaskResult(BaseModel):
    task_id: str
    status: str
    created_at: datetime


# --------------------------------------------------
# 模擬 AI 推論（正式環境換成真正的模型呼叫）
# --------------------------------------------------
def fake_ai_predict(features: dict) -> dict:
    """模擬 AI 模型回傳結果"""
    avg_conf = features.get("avg_confidence", 0.5)
    total = features.get("total_amount", 0)

    # 簡單規則模擬模型行為
    if total > 2000 and avg_conf < 0.7:
        return {"label": "high_risk", "confidence": 0.85}
    elif total > 1000:
        return {"label": "medium_risk", "confidence": 0.65}
    else:
        return {"label": "low_risk", "confidence": 0.92}


def fake_llm_summarize(data: dict) -> str:
    """模擬 LLM 把結構化資料轉成自然語言"""
    return (
        f"使用者 {data['user_id']} 共有 {data['total_events']} 筆交易，"
        f"總金額 {data['total_amount']}，"
        f"平均信心值 {data['avg_confidence']}。"
    )


# --------------------------------------------------
# Service
# --------------------------------------------------
def prepare_features(user_id: int) -> dict:
    """從 Event Store 整理特徵，給 AI 用"""
    df = pd.read_csv(DATA_PATH)
    user_df = df[df["user_id"] == user_id]

    if user_df.empty:
        return {"user_id": user_id, "total_events": 0,
                "total_amount": 0, "avg_confidence": None}

    return {
        "user_id": user_id,
        "total_events": len(user_df),
        "total_amount": float(user_df["amount"].sum()),
        "avg_confidence": round(float(user_df["confidence"].mean()), 2),
    }


def evaluate_risk(user_id: int) -> RiskResult:
    """Pipeline 1: 推論 — 整理特徵 → AI 推論 → 防呆"""
    features = prepare_features(user_id)
    prediction = fake_ai_predict(features)

    # 防呆：低信心不自動處理
    if prediction["confidence"] >= 0.8:
        action = "auto_flag"
    elif prediction["confidence"] >= 0.6:
        action = "require_review"
    else:
        action = "defer"

    return RiskResult(
        user_id=user_id,
        risk_level=prediction["label"],
        confidence=prediction["confidence"],
        action=action,
        features=features,
    )


def summarize_user(user_id: int, use_llm: bool = False) -> SummaryResult:
    """Pipeline 2: 摘要 — Pandas 整理 → (optional) LLM 語言化"""
    features = prepare_features(user_id)

    narrative = None
    if use_llm and features["total_events"] > 0:
        narrative = fake_llm_summarize(features)

    return SummaryResult(
        user_id=user_id,
        total_events=features["total_events"],
        total_amount=features["total_amount"],
        avg_confidence=features["avg_confidence"],
        narrative=narrative,
    )


def create_review_task(user_id: int, reason: str) -> TaskResult:
    """Pipeline 3: 任務觸發 — 建立審核事件"""
    return TaskResult(
        task_id=str(uuid4())[:8],
        status="pending",
        created_at=datetime.now(),
    )


# --------------------------------------------------
# App
# --------------------------------------------------
app = FastAPI(title="LLM Pipeline Demo")


# Pipeline 1: 推論
@app.post("/risk/evaluate")
def risk_evaluate(req: RiskRequest):
    return evaluate_risk(req.user_id)


# Pipeline 2: 摘要
@app.get("/users/{user_id}/summary")
def user_summary(user_id: int, llm: bool = False):
    return summarize_user(user_id, use_llm=llm)


# Pipeline 3: 任務觸發
@app.post("/tasks/review")
def trigger_review(req: TaskRequest):
    return create_review_task(req.user_id, req.reason)
