"""
串流回應：把 LLM 的回答一段一段送出

執行：uvicorn main:app --reload
測試：curl -N http://localhost:8000/summary/123/stream
"""
import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI(title="Streaming Demo")

# 模擬 Pandas 整理好的結果（正式環境從 Event Store 算出來）
SUMMARY = {123: {"total_events": 4, "total_amount": 2500, "avg_confidence": 0.84}}


def fake_llm_chunks(user_id: int) -> list[str]:
    """模擬 LLM 一次吐出一小段文字"""
    s = SUMMARY[user_id]
    return [
        f"使用者 {user_id} ",
        f"共有 {s['total_events']} 筆事件，",
        f"總金額 {s['total_amount']}，",
        f"平均信心值 {s['avg_confidence']}。",
    ]


# --------------------------------------------------
# 一般回應：全部生完才一次送出
# --------------------------------------------------
@app.get("/summary/{user_id}")
async def summary(user_id: int):
    if user_id not in SUMMARY:
        raise HTTPException(status_code=404, detail=f"找不到使用者：{user_id}")

    chunks = fake_llm_chunks(user_id)
    await asyncio.sleep(0.5 * len(chunks))  # 模擬 LLM 慢慢生成
    return {"summary": "".join(chunks)}


# --------------------------------------------------
# 串流回應：生一段就送一段（SSE 格式：data: 內容 + 空行）
# --------------------------------------------------
@app.get("/summary/{user_id}/stream")
async def summary_stream(user_id: int):
    async def generate():
        for chunk in fake_llm_chunks(user_id):
            await asyncio.sleep(0.5)  # 用 await，不要用 time.sleep
            yield f"data: {chunk}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
