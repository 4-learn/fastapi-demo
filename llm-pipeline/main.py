"""機房感測器 Pipeline Demo。模型與 LLM 都是模擬，不控制真實設備。"""
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

DATA_PATH = Path(__file__).parent / "events.csv"
# 任務只保存在這個 process 的記憶體，不會自動執行；重啟會消失。
tasks = []


class RiskRequest(BaseModel):
    sensor_id: str = Field(min_length=1)


class RiskResult(BaseModel):
    sensor_id: str
    risk_level: str
    confidence: float | None
    action: str
    features: dict


class SummaryResult(BaseModel):
    sensor_id: str
    total_readings: int
    avg_temperature: float | None
    max_temperature: float | None
    avg_humidity: float | None
    narrative: str | None = None


class TaskRequest(BaseModel):
    sensor_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class TaskResult(BaseModel):
    task_id: str
    sensor_id: str
    reason: str
    status: str
    created_at: datetime


def prepare_features(sensor_id: str) -> dict:
    df = pd.read_csv(DATA_PATH)
    sensor_df = df[df["sensor_id"] == sensor_id]
    if sensor_df.empty:
        return {"sensor_id": sensor_id, "total_readings": 0,
                "avg_temperature": None, "max_temperature": None, "avg_humidity": None}
    return {
        "sensor_id": sensor_id,
        "total_readings": len(sensor_df),
        "avg_temperature": round(float(sensor_df["temperature"].mean()), 2),
        "max_temperature": float(sensor_df["temperature"].max()),
        "avg_humidity": round(float(sensor_df["humidity"].mean()), 2),
    }


def fake_ai_predict(features: dict) -> dict:
    """僅以固定規則模擬模型，不是訓練成果，也不是機房安全標準。"""
    temperature = features["max_temperature"]
    if temperature >= 35:
        return {"label": "high_risk", "confidence": 0.85}
    if temperature >= 30:
        return {"label": "medium_risk", "confidence": 0.65}
    return {"label": "low_risk", "confidence": 0.92}


def fake_llm_summarize(data: dict) -> str:
    """固定字串模擬語言化；沒有呼叫外部 LLM。"""
    return (
        f"感測器 {data['sensor_id']} 共有 {data['total_readings']} 筆讀數，"
        f"平均溫度 {data['avg_temperature']} 度，最高溫度 {data['max_temperature']} 度，"
        f"平均濕度 {data['avg_humidity']}%。"
    )


def evaluate_risk(sensor_id: str) -> RiskResult:
    features = prepare_features(sensor_id)
    if features["total_readings"] == 0:
        return RiskResult(sensor_id=sensor_id, risk_level="unknown", confidence=None,
                          action="defer", features=features)
    prediction = fake_ai_predict(features)
    if prediction["label"] == "low_risk":
        action = "none"
    elif prediction["label"] == "high_risk" and prediction["confidence"] >= 0.8:
        action = "auto_alert"
    elif prediction["confidence"] >= 0.6:
        action = "require_review"
    else:
        action = "defer"
    # 只回傳建議，沒有真的發通知或控制設備。
    return RiskResult(sensor_id=sensor_id, risk_level=prediction["label"],
                      confidence=prediction["confidence"], action=action, features=features)


def summarize_sensor(sensor_id: str, use_llm: bool = False) -> SummaryResult:
    features = prepare_features(sensor_id)
    narrative = None
    if use_llm and features["total_readings"] > 0:
        narrative = fake_llm_summarize(features)
    return SummaryResult(
        sensor_id=sensor_id,
        total_readings=features["total_readings"],
        avg_temperature=features["avg_temperature"],
        max_temperature=features["max_temperature"],
        avg_humidity=features["avg_humidity"],
        narrative=narrative,
    )


def create_review_task(sensor_id: str, reason: str) -> TaskResult:
    task = TaskResult(task_id=str(uuid4()), sensor_id=sensor_id, reason=reason,
                      status="pending", created_at=datetime.now())
    tasks.append(task)
    return task


app = FastAPI(title="Machine Room AI Pipeline Demo")


@app.post("/risk/evaluate")
def risk_evaluate(req: RiskRequest):
    return evaluate_risk(req.sensor_id)


@app.get("/sensors/{sensor_id}/summary")
def sensor_summary(sensor_id: str, llm: bool = False):
    return summarize_sensor(sensor_id, use_llm=llm)


@app.post("/tasks/review")
def trigger_review(req: TaskRequest):
    return create_review_task(req.sensor_id, req.reason)
