from fastapi import FastAPI, Body

app = FastAPI(title="Part 3：Body — 寄送資料包裹")

DRINKS = {
    "bubble-tea": {"name": "珍珠奶茶", "price": 50},
    "green-tea": {"name": "綠茶", "price": 30},
    "lemon-tea": {"name": "檸檬紅茶", "price": 40},
}

orders = []


@app.post("/orders")
def create_order(order: dict = Body(...)):
    """
    點餐：把完整訂單資料放在 Body
    Body 適合放「一包資料」，例如：
    {
        "drink_id": "bubble-tea",
        "size": "大杯",
        "ice": "少冰",
        "sugar": "半糖",
        "quantity": 2
    }
    """
    order_id = len(orders) + 1
    orders.append({"order_id": order_id, "detail": order})
    return {"message": "點餐成功", "order_id": order_id, "detail": order}


@app.post("/drinks/{drink_id}/customize")
def customize_drink(
    drink_id: str,
    debug: bool = False,
    options: dict = Body(...),
):
    """
    三層一起用：
    - Path: drink_id（哪杯飲料）
    - Query: debug（要不要看除錯資訊）
    - Body: options（客製化內容）
    """
    if drink_id not in DRINKS:
        return {"error": f"找不到飲料：{drink_id}"}

    result = {
        "drink": DRINKS[drink_id]["name"],
        "customization": options,
    }
    if debug:
        result["debug"] = {"raw_drink_id": drink_id, "raw_options": options}
    return result
