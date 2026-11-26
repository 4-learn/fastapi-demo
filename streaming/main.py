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


def fake_llm_chunks(location: str) -> list[str]:
    """模擬 LLM 一次吐出一小段文字"""
    s = SUMMARY[location]
    return [
        f"位置 {location} ",
        f"共有 {s['total_events']} 筆通道阻塞事件，",
        f"累計阻塞秒數 {s['total_duration_seconds']}，",
        f"平均信心值 {s['avg_confidence']}。",
    ]


# --------------------------------------------------
# 一般回應：全部生完才一次送出
# --------------------------------------------------
@app.get("/summary/{location}")
async def summary(location: str):
    if location not in SUMMARY:
        raise HTTPException(status_code=404, detail=f"找不到位置：{location}")

    chunks = fake_llm_chunks(location)
    await asyncio.sleep(0.5 * len(chunks))  # 模擬 LLM 慢慢生成
    return {"summary": "".join(chunks)}


# --------------------------------------------------
# 串流回應：生一段就送一段（SSE 格式：data: 內容 + 空行）
# --------------------------------------------------
@app.get("/summary/{location}/stream")
async def summary_stream(location: str):
    async def generate():
        for chunk in fake_llm_chunks(location):
            await asyncio.sleep(0.5)  # 用 await，不要用 time.sleep
            yield f"data: {chunk}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
