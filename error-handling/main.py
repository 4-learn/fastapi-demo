from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime


# --------------------------------------------------
# 自訂 Exception
# --------------------------------------------------
class EventRejected(Exception):
    """事件被系統拒絕（格式正確但邏輯不接受）"""
    def __init__(self, reason: str, event_type: str = "unknown"):
        self.reason = reason
        self.event_type = event_type


class EventNotFound(Exception):
    """事件對象不存在"""
    def __init__(self, reason: str):
        self.reason = reason


# --------------------------------------------------
# Schema
# --------------------------------------------------
class EventPayload(BaseModel):
    user_id: int = Field(gt=0)
    timestamp: datetime
    payload: Dict[str, Any]


# --------------------------------------------------
# App
# --------------------------------------------------
app = FastAPI(title="Error Handling Demo")

SUPPORTED_TYPES = {"click", "transaction", "login"}
KNOWN_USERS = {1, 2, 3, 100, 123}


# --------------------------------------------------
# Exception Handlers
# --------------------------------------------------
@app.exception_handler(EventRejected)
async def handle_event_rejected(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "status": "rejected",
            "event_type": exc.event_type,
            "reason": exc.reason
        }
    )


@app.exception_handler(EventNotFound)
async def handle_event_not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "status": "rejected",
            "reason": exc.reason
        }
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "status": "rejected",
            "reason": "Event does not match schema",
            "details": exc.errors()
        }
    )


# --------------------------------------------------
# Endpoint
# --------------------------------------------------
@app.post("/events/{event_type}")
def receive_event(event_type: str, event: EventPayload):
    if event_type not in SUPPORTED_TYPES:
        raise EventRejected(
            reason=f"Unsupported event type: {event_type}",
            event_type=event_type
        )

    if event.user_id not in KNOWN_USERS:
        raise EventNotFound(
            reason=f"User {event.user_id} not found"
        )

    return {
        "status": "accepted",
        "event_type": event_type,
        "event": event.model_dump()
    }
