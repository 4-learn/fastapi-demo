"""
PostgreSQL + ORM（一）：連線與資料表模型

執行：python main.py
"""
import os
from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


# --------------------------------------------------
# 連線：從環境變數讀，沒設定就用課堂預設值
# --------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/events",
)
engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# 資料表模型：一個 class = 一張表，一個屬性 = 一個欄位
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
# 建表：教學用，每次執行都先刪掉再重建，輸出才會一樣
# --------------------------------------------------
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
print("1. 建立資料表 events")
print("---")


# --------------------------------------------------
# 新增：建立物件 → add → commit
# --------------------------------------------------
with Session(engine) as session:
    session.add(Event(
        event_type="login",
        user_id=123,
        timestamp=datetime(2025, 1, 10, 9, 0),
        payload={"device": "mobile"},
    ))
    session.add(Event(
        event_type="transaction",
        user_id=123,
        timestamp=datetime(2025, 1, 10, 10, 30),
        payload={"amount": 500},
    ))
    session.add(Event(
        event_type="login",
        user_id=456,
        timestamp=datetime(2025, 1, 10, 9, 15),
        payload={"device": "web"},
    ))
    session.commit()
print("2. 新增 3 筆事件")
print("---")


# --------------------------------------------------
# 查詢：select → where → 執行
# --------------------------------------------------
with Session(engine) as session:
    stmt = select(Event).where(Event.user_id == 123).order_by(Event.timestamp)
    events = session.scalars(stmt).all()

print("3. user_id = 123 的事件：")
for e in events:
    print(e.id, e.event_type, e.timestamp, e.payload)

engine.dispose()  # 用完把連線關掉
