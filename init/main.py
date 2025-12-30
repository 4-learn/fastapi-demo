from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello FastAPI"}

@app.post("/echo")
def echo(data: dict):
    return {
        "received": data
    }
