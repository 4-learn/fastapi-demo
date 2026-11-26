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
    event_id: str
    event_type: str
    location: str
    duration_seconds: float = Field(ge=0)
    confidence: float = Field(ge=0, le=1)


class RiskResult(BaseModel):
    event_id: str
    location: str
    risk_level: str
    confidence: float
    action: str
    features: dict


class SummaryResult(BaseModel):
    location: str
    total_events: int
    total_duration_seconds: float
    avg_confidence: float | None
    narrative: str | None = None


class TaskRequest(BaseModel):
    event_id: str
    reason: str


class TaskResult(BaseModel):
    task_id: str
    event_id: str
    reason: str
    status: str
    created_at: datetime


# --------------------------------------------------
# 模擬 AI 推論（正式環境換成真正的模型呼叫）
# --------------------------------------------------
def fake_ai_predict(features: dict) -> dict:
    """模擬 AI 模型回傳結果"""
    # 單筆通道阻塞的教學假規則，不是真實模型或安全標準。
    if features["event_type"] != "aisle_blocked":
        label = "low_risk"
    elif features["duration_seconds"] > 120:
        label = "high_risk"
    else:
        label = "medium_risk"
    return {"label": label, "confidence": features["confidence"]}


def fake_llm_summarize(data: dict) -> str:
    """模擬 LLM 把結構化資料轉成自然語言"""
    return (
        f"位置 {data['location']} 共有 {data['total_events']} 筆通道阻塞事件，"
        f"累計阻塞秒數 {data['total_duration_seconds']}，"
        f"平均信心值 {data['avg_confidence']}。"
    )


# --------------------------------------------------
# Service
# --------------------------------------------------
def prepare_features(location: str) -> dict:
    """從 Event Store 整理特徵，給 AI 用（只算通道阻塞事件）"""
    df = pd.read_csv(DATA_PATH)
    location_df = df[(df["location"] == location) & (df["event_type"] == "aisle_blocked")]

    if location_df.empty:
        return {"location": location, "total_events": 0,
                "total_duration_seconds": 0, "avg_confidence": None}

    return {
        "location": location,
        "total_events": len(location_df),
        "total_duration_seconds": float(location_df["duration_seconds"].sum()),
        "avg_confidence": round(float(location_df["confidence"].mean()), 2),
    }


def evaluate_risk(event: RiskRequest) -> RiskResult:
    """Pipeline 1：評估單筆事件，不查位置歷史。"""
    features = {
        "event_type": event.event_type,
        "duration_seconds": event.duration_seconds,
        "confidence": event.confidence,
    }
    prediction = fake_ai_predict(features)

    # 防呆：只有高風險才可能自動處理，低信心不自動處理
    if prediction["label"] == "low_risk":
        action = "none"             # 低風險：不用處理
    elif prediction["label"] == "high_risk" and prediction["confidence"] >= 0.8:
        action = "auto_flag"        # 高風險且模型有把握：自動標記
    elif prediction["confidence"] >= 0.6:
        action = "require_review"   # 有疑慮：交給人審核
    else:
        action = "defer"            # 模型沒把握：先不決定

    return RiskResult(
        event_id=event.event_id,
        location=event.location,
        risk_level=prediction["label"],
        confidence=prediction["confidence"],
        action=action,
        features=features,
    )


def summarize_location(location: str, use_llm: bool = False) -> SummaryResult:
    """Pipeline 2: 摘要 — Pandas 整理 → (optional) LLM 語言化"""
    features = prepare_features(location)

    narrative = None
    if use_llm and features["total_events"] > 0:
        narrative = fake_llm_summarize(features)

    return SummaryResult(
        location=location,
        total_events=features["total_events"],
        total_duration_seconds=features["total_duration_seconds"],
        avg_confidence=features["avg_confidence"],
        narrative=narrative,
    )


def create_review_task(event_id: str, reason: str) -> TaskResult:
    """Pipeline 3: 任務觸發 — 建立審核事件"""
    return TaskResult(
        task_id=str(uuid4())[:8],
        event_id=event_id,
        reason=reason,
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
    return evaluate_risk(req)


# Pipeline 2: 摘要
@app.get("/locations/{location}/summary")
def location_summary(location: str, llm: bool = False):
    return summarize_location(location, use_llm=llm)


# Pipeline 3: 任務觸發
@app.post("/tasks/review")
def trigger_review(req: TaskRequest):
    return create_review_task(req.event_id, req.reason)
