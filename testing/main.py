"""
API 自動測試：被測試的程式（沿用 ORM（二）Workshop 完成後的版本）

執行測試：pytest -v
"""
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import JSON, DateTime, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


# --------------------------------------------------
# 連線
# --------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/events",
)
engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# 資料表模型（資料庫裡長什麼樣子）
# --------------------------------------------------
class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(50))
    user_id: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    payload: Mapped[dict] = mapped_column(JSON)


# --------------------------------------------------
# Schema（API 對外長什麼樣子）
# --------------------------------------------------
class EventPayload(BaseModel):
    user_id: int = Field(gt=0)
    timestamp: datetime
    payload: Dict[str, Any]


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 可以直接吃 ORM 物件

    id: int
    event_type: str
    user_id: int
    timestamp: datetime
    payload: Dict[str, Any]


# --------------------------------------------------
# 每個 request 拿一個 session，用完自動關掉
# --------------------------------------------------
def get_db():
    with Session(engine) as session:
        yield session


# --------------------------------------------------
# App：啟動時建表（表已存在就跳過）
# --------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Event API + PostgreSQL", lifespan=lifespan)


@app.post("/events/{event_type}", response_model=EventOut, status_code=201)
def create_event(event_type: str, event: EventPayload, db: Session = Depends(get_db)):
    row = Event(
        event_type=event_type,
        user_id=event.user_id,
        timestamp=event.timestamp,
        payload=event.payload,
    )
    db.add(row)
    db.commit()
    db.refresh(row)  # 拿回資料庫產生的 id
    return row


@app.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    row = db.get(Event, event_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"找不到事件：{event_id}")
    return row


@app.get("/events", response_model=list[EventOut])
def list_events(user_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Event).order_by(Event.id)
    if user_id is not None:
        stmt = stmt.where(Event.user_id == user_id)
    return db.scalars(stmt).all()


@app.get("/users/{user_id}/events/count")
def count_events(user_id: int, db: Session = Depends(get_db)):
    stmt = select(func.count()).select_from(Event).where(Event.user_id == user_id)
    return {"user_id": user_id, "count": db.scalar(stmt)}
