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
    {"name": "手沖濾掛咖啡", "price": 50, "category": "飲料類"},
    {"name": "美式咖啡", "price": 50, "category": "飲料類"},
    {"name": "果汁", "price": 50, "category": "飲料類"},
    {"name": "桂花烏龍茶", "price": 30, "category": "飲料類"},
    {"name": "菊花普洱茶", "price": 30, "category": "飲料類"},
    {"name": "阿里山紅烏龍茶", "price": 30, "category": "飲料類"},
    {"name": "青醬義大利麵", "price": 110, "image": "青醬義大利麵.jpg", "category": "義大利麵類"},
    {"name": "紅醬義大利麵", "price": 115, "image": "紅醬義大利麵.jpg", "category": "義大利麵類"},
    {"name": "海鮮pizza", "price": 150, "image": "海鮮pizza.jpg", "category": "Pizza類"},
    {"name": "總匯pizza", "price": 160, "image": "總匯pizza.jpg", "category": "Pizza類"},
    {"name": "厚片吐司", "price": 160, "image": "厚片土司.jpg", "category": "下午茶類"},
    {"name": "阿里山烏龍茶", "price": 30, "category": "飲料類"},
    {"name": "玫瑰紅茶", "price": 30, "category": "飲料類"},
    {"name": "芭樂心葉茶", "price": 30, "category": "飲料類"},
    {"name": "即溶咖啡(二合一)", "price": 30, "category": "飲料類"},
    {"name": "即溶咖啡(三合一)", "price": 30, "category": "飲料類"},
    {"name": "奶茶(原味)", "price": 30, "category": "飲料類"},
    {"name": "奶茶(杏仁)", "price": 30, "category": "飲料類"},
    {"name": "莓果茶", "price": 30, "category": "飲料類"}
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
    total_drink_qty = 0
    drink_items = []
    total = 0

    for item in menu:
        qty_str = request.form.get(f'quantity_{item["name"]}', '0')
        try:
            qty = int(qty_str) if qty_str.strip() else 0
        except ValueError:
            qty = 0

        if qty <= 0:
            continue

        # 建立餐點資料
        item_entry = {
            "name": item["name"],
            "price": item["price"],
            "quantity": qty,
            "category": item["category"],
            "done": False
        }

        # 若是主餐類，加上 done_list
        if item["category"] != "飲料類":
            total_main_qty += qty
            item_entry["done_list"] = [False] * qty
        else:
            total_drink_qty += qty
            for _ in range(qty):
                drink_items.append(item)

        order_items.append(item_entry)

    # 檢查飲料是否足夠
    if total_drink_qty < total_main_qty:
        flash(f"您點了 {total_main_qty} 份主餐，但只選擇了 {total_drink_qty} 杯飲料，請至少選擇等量的飲料！")
        return render_template('index.html', menu=menu, drinks=drinks, form_data=request.form)

    # 折抵邏輯：飲料由高到低排序，每份主餐折抵 30 元
    remaining_discount = total_main_qty * 30
    drink_total = 0
    sorted_drinks = sorted(drink_items, key=lambda d: d["price"], reverse=True)

    for drink in sorted_drinks:
        price = drink["price"]
        if remaining_discount >= price:
            remaining_discount -= price
        else:
            discount = min(price, remaining_discount)
            drink_total += price - discount
            remaining_discount -= discount
    total += drink_total

    # 加總主餐價格
    for item in order_items:
        if item["category"] != "飲料類":
            total += item["price"] * item["quantity"]

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

@app.route('/mark_item_done/<int:order_id>/<int:item_index>/<int:portion_index>', methods=['POST'])
@requires_auth
def mark_item_done(order_id, item_index, portion_index):
    for order in orders:
        if order["id"] == order_id:
            if 0 <= item_index < len(order["items"]):
                item = order["items"][item_index]
                # ✅ 向下相容處理
                if "done_list" not in item:
                    item["done_list"] = [False] * item["quantity"]
                if 0 <= portion_index < len(item["done_list"]):
                    item["done_list"][portion_index] = True
                if all(item["done_list"]):
                    item["done"] = True
                if all(i.get("done") for i in order["items"]):
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
