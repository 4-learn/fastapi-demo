"""
串流回應：把 LLM 的回答一段一段送出

執行：uvicorn main:app --reload
測試：curl -N http://localhost:8000/summary/aisle_01/stream
"""
import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI(title="Streaming Demo")

# 模擬 Pandas 整理好的結果（正式環境從 Event Store 算出來）
SUMMARY = {"aisle_01": {"total_events": 3, "total_duration_seconds": 2500, "avg_confidence": 0.79}}


async def fake_llm_chunks(location: str):
    """模擬上游 LLM 串流：等待後逐段 yield，不一次回傳完整 list。"""
    s = SUMMARY[location]
    chunks = [
        f"位置 {location} ",
        f"共有 {s['total_events']} 筆通道阻塞事件，",
        f"累計阻塞秒數 {s['total_duration_seconds']}，",
        f"平均信心值 {s['avg_confidence']}。",
    ]
    for chunk in chunks:
        await asyncio.sleep(0.5)  # 模擬等待上游生成下一段
        yield chunk


# --------------------------------------------------
# 一般回應：全部生完才一次送出
# --------------------------------------------------
@app.get("/summary/{location}")
async def summary(location: str):
    if location not in SUMMARY:
        raise HTTPException(status_code=404, detail=f"找不到位置：{location}")

    chunks = []
    async for chunk in fake_llm_chunks(location):
        chunks.append(chunk)  # 一般回應：先收齊，再一次回傳
    return {"summary": "".join(chunks)}


# --------------------------------------------------
# 串流回應：生一段就送一段（SSE 格式：data: 內容 + 空行）
# --------------------------------------------------
@app.get("/summary/{location}/stream")
async def summary_stream(location: str):
    async def generate():
        async for chunk in fake_llm_chunks(location):
            # 收到上游一段，就轉送一段，不先收集全部內容。
            yield f"data: {chunk}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
