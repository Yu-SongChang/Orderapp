from flask import Flask, render_template, request, redirect, url_for, Response, flash
from datetime import datetime
from functools import wraps
import os
from collections import defaultdict

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'

USERNAME = 'admin'
PASSWORD = '1234'

menu = [
    {"name": "咖哩雞排飯", "price": 130, "image": "咖哩雞排飯.jpg", "category": "咖哩飯類"},
    {"name": "咖哩豬排飯", "price": 125, "image": "咖哩豬排飯.jpg", "category": "咖哩飯類"},
    {"name": "咖啡", "price": 50, "category": "飲料類"},
    {"name": "拉花咖啡", "price": 65, "category": "飲料類"},
    {"name": "普洱茶", "price": 45, "category": "飲料類"},
    {"name": "紅烏龍茶", "price": 45, "category": "飲料類"},
    {"name": "青醬義大利麵", "price": 110, "image": "青醬義大利麵.jpg", "category": "義大利麵類"},
    {"name": "紅醬義大利麵", "price": 115, "image": "紅醬義大利麵.jpg", "category": "義大利麵類"},
    {"name": "海鮮pizza", "price": 150, "image": "海鮮pizza.jpg", "category": "Pizza類"},
    {"name": "總匯pizza", "price": 160, "image": "總匯pizza.jpg", "category": "Pizza類"},
    {"name": "厚片吐司", "price": 160, "image": "厚片土司.jpg", "category": "下午茶類"}
]

orders = []
drinks = [item for item in menu if item["category"] == "飲料類"]

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response('需要帳號密碼才能查看此頁面。', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('index.html', menu=menu, drinks=drinks, request_form=request.form)

@app.route('/submit_order', methods=['POST'])
def submit_order():
    order_items = []
    total_main_qty = 0
    attached_drinks = []
    total = 0

    for item in menu:
        qty_str = request.form.get(f'quantity_{item["name"]}', '0')
        try:
            qty = int(qty_str) if qty_str.strip() else 0
        except ValueError:
            qty = 0

        if qty <= 0:
            continue

        if item["category"] != "飲料類":
            drinks_for_meal = []
            for drink in drinks:
                drink_qty_key = f"drink_for_{item['name']}_{drink['name']}"
                drink_qty = int(request.form.get(drink_qty_key, 0))
                for _ in range(drink_qty):
                    drinks_for_meal.append(drink)
            attached_drinks.extend(drinks_for_meal)
            total_main_qty += qty
            order_items.append({
                "name": item["name"],
                "price": item["price"],
                "quantity": qty,
                "category": item["category"],
                "done": False,
                "drinks": drinks_for_meal
            })
        else:
            drink_qty = int(request.form.get(f'quantity_{item["name"]}', 0))
            if drink_qty > 0:
                order_items.append({
                    "name": item["name"],
                    "price": item["price"],
                    "quantity": drink_qty,
                    "category": item["category"],
                    "done": False
                })
                total += item["price"] * drink_qty

    if len(attached_drinks) < total_main_qty:
        flash(f"您點了 {total_main_qty} 份主餐，但只選擇了 {len(attached_drinks)} 杯附餐飲料，請至少選擇等量的飲料！")
        return render_template('index.html', menu=menu, drinks=drinks, form_data=request.form)

    # 折抵邏輯修正：飲料由高至低價格排序，抵扣30元/主餐
    remaining_discount = total_main_qty * 30
    sorted_attached_drinks = sorted(attached_drinks, key=lambda d: d["price"], reverse=True)
    drink_total = 0

    for drink in sorted_attached_drinks:
        if remaining_discount >= drink["price"]:
            remaining_discount -= drink["price"]
        else:
            discount = min(drink["price"], remaining_discount)
            drink_total += drink["price"] - discount
            remaining_discount -= discount

    # 加總主餐價格
    for item in order_items:
        if item["category"] != "飲料類":
            total += item["price"] * item["quantity"]
    total += drink_total

    if order_items:
        new_order = {
            "id": len(orders) + 1,
            "items": order_items,
            "total": total,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed": False
        }
        orders.append(new_order)
        return redirect(url_for('choose_payment', order_id=new_order["id"]))
    return redirect(url_for('index'))

@app.route('/choose_payment/<int:order_id>')
def choose_payment(order_id):
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return redirect(url_for('index'))
    return render_template('choose_payment.html', order=order)

@app.route('/transfer_payment/<int:order_id>')
def transfer_payment(order_id):
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return redirect(url_for('index'))
    return render_template('transfer_payment.html', order=order)

@app.route('/bank_transfer/<int:order_id>')
def bank_transfer(order_id):
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return redirect(url_for('index'))
    return render_template('bank_transfer.html', order=order)

@app.route('/order_status')
def order_status():
    order_id = request.args.get('order_id', type=int)
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return redirect(url_for('index'))
    return render_template('order_status.html', order=order)

@app.route('/admin')
@requires_auth
def admin():
    today = datetime.now().strftime("%Y-%m-%d")
    today_orders = [o for o in orders if o["timestamp"].startswith(today)]
    today_total = sum(o["total"] for o in today_orders)

    drink_summary = defaultdict(int)
    for order in orders:
        for item in order["items"]:
            if item.get("category") == "飲料類":
                drink_summary[item["name"]] += item["quantity"]
            elif "drinks" in item:
                for d in item["drinks"]:
                    drink_summary[d["name"]] += 1

    return render_template('admin.html', orders=orders, today_total=today_total, drink_summary=drink_summary)

@app.route('/mark_completed/<int:order_id>', methods=['POST'])
@requires_auth
def mark_completed(order_id):
    for order in orders:
        if order["id"] == order_id:
            for item in order["items"]:
                item["done"] = True
            order["completed"] = True
            break
    return redirect(url_for('admin'))

@app.route('/mark_item_done/<int:order_id>/<int:item_index>', methods=['POST'])
@requires_auth
def mark_item_done(order_id, item_index):
    for order in orders:
        if order["id"] == order_id:
            if 0 <= item_index < len(order["items"]):
                order["items"][item_index]["done"] = True
            if all(item["done"] for item in order["items"]):
                order["completed"] = True
            break
    return redirect(url_for('admin'))

@app.route('/delete_order/<int:order_id>', methods=['POST'])
@requires_auth
def delete_order(order_id):
    global orders
    orders = [o for o in orders if o["id"] != order_id]
    return redirect(url_for('admin'))

@app.route('/clear_orders', methods=['POST'])
@requires_auth
def clear_orders():
    orders.clear()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
