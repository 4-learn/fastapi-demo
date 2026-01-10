from fastapi import FastAPI
from tasks import sync_infinite_loop, async_infinite_loop

app = FastAPI()


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.get("/sync")
async def sync_api():
    """async 裡用 time.sleep - 會阻塞 event loop"""
    sync_infinite_loop()
    return {"message": "done"}


@app.get("/async")
async def async_api():
    """異步 API - 不會阻塞"""
    await async_infinite_loop()
    return {"message": "done"}
