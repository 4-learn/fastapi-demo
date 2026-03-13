from fastapi import FastAPI
import time
import asyncio

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"status": "pong"}

@app.get("/sync")
async def sync_api():
    time.sleep(10)
    return {"status": "done"}

@app.get("/async")
async def async_api():
    await asyncio.sleep(10)
    return {"status": "done"}
