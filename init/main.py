from fastapi import FastAPI, Body

app = FastAPI()

@app.get("/")
def root():
    return {"message": "alive"}

@app.post("/echo")
def echo(data: dict = Body()):
    return {"received": data}
