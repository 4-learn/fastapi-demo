from fastapi import FastAPI

app = FastAPI(title="Part 2：Query — 篩選與選項")

DRINKS = {
    "bubble-tea": {"name": "珍珠奶茶", "price": 50, "category": "奶茶"},
    "green-tea": {"name": "綠茶", "price": 30, "category": "茶"},
    "lemon-tea": {"name": "檸檬紅茶", "price": 40, "category": "茶"},
    "cocoa": {"name": "可可", "price": 55, "category": "奶茶"},
}


@app.get("/drinks")
def list_drinks(category: str = None, max_price: int = None):
    """
    用 Query 篩選飲料
    - category: 只看某類（茶、奶茶）
    - max_price: 價格上限
    拿掉這些條件，飲料還是飲料 → 所以是 Query
    """
    results = {}
    for drink_id, info in DRINKS.items():
        if category and info["category"] != category:
            continue
        if max_price and info["price"] > max_price:
            continue
        results[drink_id] = info
    return results


@app.get("/drinks/{drink_id}")
def get_drink(drink_id: str, show_price: bool = True):
    """
    show_price 只是「要不要顯示價格」，不影響飲料本身
    → 觀察條件，放 Query
    """
    if drink_id not in DRINKS:
        return {"error": f"找不到飲料：{drink_id}"}
    drink = {"drink_id": drink_id, "name": DRINKS[drink_id]["name"]}
    if show_price:
        drink["price"] = DRINKS[drink_id]["price"]
    return drink
