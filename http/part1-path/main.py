from fastapi import FastAPI

app = FastAPI(title="Part 1：Path — 資源的身份證")

# 飲料菜單（模擬資料庫）
DRINKS = {
    "bubble-tea": {"name": "珍珠奶茶", "price": 50},
    "green-tea": {"name": "綠茶", "price": 30},
    "lemon-tea": {"name": "檸檬紅茶", "price": 40},
}


@app.get("/drinks")
def list_drinks():
    """列出所有飲料"""
    return DRINKS


@app.get("/drinks/{drink_id}")
def get_drink(drink_id: str):
    """
    用 Path 指定「哪一杯」
    drink_id 就是這杯飲料的身份證
    """
    if drink_id not in DRINKS:
        return {"error": f"找不到飲料：{drink_id}"}
    drink = DRINKS[drink_id]
    return {"drink_id": drink_id, "name": drink["name"], "price": drink["price"]}
