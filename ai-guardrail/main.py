from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# --------------------------------------------------
# AI 模型的輸出結構
# --------------------------------------------------
class Prediction(BaseModel):
    """模型回傳的原始判斷"""
    label: str
    confidence: float = Field(ge=0.0, le=1.0)


# --------------------------------------------------
# 系統決策結構
# --------------------------------------------------
class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Action(str, Enum):
    AUTO_BLOCK = "auto_block"
    REQUIRE_REVIEW = "require_review"
    DEFER = "defer"


class DecisionResponse(BaseModel):
    """系統根據 AI 輸出做出的決策"""
    prediction: str
    confidence: float
    risk_level: RiskLevel
    action: Action
    reason: str


class DecisionEvent(BaseModel):
    """決策事件：把每次判斷記錄下來"""
    event_type: str = "ai_decision"
    source_event_id: str
    prediction: str
    confidence: float
    risk_level: str
    action: str
    timestamp: datetime


# --------------------------------------------------
# Guardrail Service
# --------------------------------------------------
# 門檻值：集中管理，不散落在 if/else 裡
THRESHOLDS = {
    "auto": 0.9,
    "review": 0.6,
}


def evaluate(prediction: Prediction) -> DecisionResponse:
    """
    根據模型輸出的 confidence，決定系統行動。

    模型負責算，系統負責決定。
    """
    if prediction.confidence >= THRESHOLDS["auto"]:
        return DecisionResponse(
            prediction=prediction.label,
            confidence=prediction.confidence,
            risk_level=RiskLevel.HIGH,
            action=Action.AUTO_BLOCK,
            reason="信心值足夠，系統自動處理",
        )

    if prediction.confidence >= THRESHOLDS["review"]:
        return DecisionResponse(
            prediction=prediction.label,
            confidence=prediction.confidence,
            risk_level=RiskLevel.MEDIUM,
            action=Action.REQUIRE_REVIEW,
            reason="信心值不足以自動處理，轉人工審核",
        )

    return DecisionResponse(
        prediction=prediction.label,
        confidence=prediction.confidence,
        risk_level=RiskLevel.LOW,
        action=Action.DEFER,
        reason="信心值過低，系統不做判斷",
    )


def to_event(source_event_id: str, decision: DecisionResponse) -> DecisionEvent:
    """把決策轉成可追蹤的事件"""
    return DecisionEvent(
        source_event_id=source_event_id,
        prediction=decision.prediction,
        confidence=decision.confidence,
        risk_level=decision.risk_level.value,
        action=decision.action.value,
        timestamp=datetime.now(),
    )


# --------------------------------------------------
# App
# --------------------------------------------------
app = FastAPI(title="AI Guardrail Demo")


class EventBody(BaseModel):
    event_id: str
    prediction: Prediction


@app.post("/evaluate")
def evaluate_prediction(body: EventBody):
    # 1. 模型已經算完，拿到 prediction
    # 2. 系統根據 confidence 決定行動
    decision = evaluate(body.prediction)

    # 3. 把決策記錄成事件
    event = to_event(body.event_id, decision)

    return {
        "decision": decision.model_dump(),
        "event": event.model_dump(),
    }


@app.get("/thresholds")
def get_thresholds():
    """查看目前的門檻設定"""
    return THRESHOLDS
