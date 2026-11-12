"""
檔案上傳：UploadFile

執行：uvicorn main:app --reload
測試：curl -F "file=@events.csv" http://localhost:8000/events/upload
"""
import io

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile

app = FastAPI(title="Upload Demo")

REQUIRED_COLUMNS = {"event_id", "user_id", "event_type", "amount", "confidence", "timestamp"}


@app.post("/events/upload")
async def upload_events(file: UploadFile):
    # 1. 只收 CSV
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="只接受 .csv 檔")

    # 2. 讀進記憶體，交給 Pandas
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    # 3. 欄位不齊就拒收
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"缺少欄位：{sorted(missing)}")

    # 4. 回傳整理結果
    return {
        "filename": file.filename,
        "rows": len(df),
        "users": sorted(int(u) for u in df["user_id"].unique()),
        "event_types": {k: int(v) for k, v in df["event_type"].value_counts().items()},
    }
