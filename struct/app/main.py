from fastapi import FastAPI

from app.routers import events

app = FastAPI(title="Event API System")

app.include_router(events.router)
