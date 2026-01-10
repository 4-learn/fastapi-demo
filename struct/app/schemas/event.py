from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class EventPayload(BaseModel):
    user_id: int = Field(gt=0)
    timestamp: datetime
    payload: Dict[str, Any]
