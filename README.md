# FastAPI × AI 系統實戰：範例程式

本專案是各章節獨立執行的範例；講義索引見 [docs/README.md](docs/README.md)。建議使用 **Python 3.12**。不需要 Poetry。

## 建立環境

```bash
cd /home/yillkid/workspace/fastapi-demo  # 或換成你 clone 的目錄
python3.12 -m venv .venv
source .venv/bin/activate              # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` 只列出範例直接用到的套件：FastAPI、Uvicorn、Pandas；Pydantic 由 FastAPI 安裝。要跑本機 API 測試再安裝 `python -m pip install -r requirements-dev.txt`（包含 pytest、httpx）。若本機的 Python 3.12 指令是 `python3`，請以 `python3 -m venv .venv` 取代上面的 `python3.12`。

## 啟動範例

```bash
cd init
python -m uvicorn main:app --reload
```

在瀏覽器開啟 <http://127.0.0.1:8000/docs>。其他章節先回到專案根目錄，再進入目標資料夾執行；模組化範例請從 `struct/` 執行 `python -m uvicorn app.main:app --reload`。非同步示範請參考 [async/async-demo/README.md](async/async-demo/README.md)，**不要對公開網路啟動阻塞範例**。

停止虛擬環境：`deactivate`。`.venv/` 已加入 `.gitignore`，不要提交環境目錄。更新依賴時修改根目錄的 `requirements.txt` / `requirements-dev.txt`，不要用 `pip freeze` 把整個環境（含間接依賴）當作直接依賴清單。
