"""
API 自動測試

執行：pytest -v
測試用的資料庫是 events_test，不會動到上課用的 events。
"""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/events_test",
)
# 保護教學預設：只允許專用 events_test，避免刪到 events。
if make_url(TEST_DATABASE_URL).database != "events_test":
    raise RuntimeError("測試只允許使用 events_test 資料庫")

# 必須先設定再 import：lifespan 也要連到測試資料庫。
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
from main import Base, app, get_db

test_engine = create_engine(TEST_DATABASE_URL)


# --------------------------------------------------
# 把 get_db 換成「連到測試資料庫」的版本
# --------------------------------------------------
def get_test_db():
    with Session(test_engine) as session:
        yield session


# --------------------------------------------------
# 每個測試開始前：清空資料表，從乾淨的狀態開始
# --------------------------------------------------
@pytest.fixture
def client():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = get_test_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


EVENT = {"user_id": 123, "timestamp": "2025-01-10T12:00:00", "payload": {"amount": 1200}}


def test_create_event(client):
    r = client.post("/events/transaction", json=EVENT)
    assert r.status_code == 201
    assert r.json()["id"] == 1
    assert r.json()["event_type"] == "transaction"


def test_get_event(client):
    client.post("/events/transaction", json=EVENT)
    r = client.get("/events/1")
    assert r.status_code == 200
    assert r.json()["payload"] == {"amount": 1200}


def test_get_missing_event(client):
    r = client.get("/events/99")
    assert r.status_code == 404
    assert r.json() == {"detail": "找不到事件：99"}


def test_invalid_user_id(client):
    invalid_event = EVENT.copy()
    invalid_event["user_id"] = 0
    r = client.post("/events/login", json=invalid_event)
    assert r.status_code == 422
