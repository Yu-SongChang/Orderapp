from flask import Flask, render_template, request, redirect, url_for, Response
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)

USERNAME = 'admin'
PASSWORD = '1234'

menu = [
    {"name": "漢堡", "price": 80, "image": "burger.jpg"},
    {"name": "炸雞", "price": 100, "image": "chicken.jpg"},
    {"name": "珍奶", "price": 60, "image": "milktea.jpg"}
]

orders = []

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        '需要帳號密碼才能查看此頁面。', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

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
    # 補齊欄位（防爆）
    for idx, order in enumerate(orders):
        if "id" not in order:
            order["id"] = idx + 1
        if "completed" not in order:
            order["completed"] = False
    return render_template('index.html', menu=menu, orders=orders)

@app.route('/submit_order', methods=['POST'])
def submit_order():
    order_items = []
    total = 0
    for item in menu:
        quantity = int(request.form.get(f'quantity_{item["name"]}', 0))
        if quantity > 0:
            subtotal = item['price'] * quantity
            total += subtotal
            order_items.append({
                "name": item['name'],
                "price": item['price'],
                "quantity": quantity
            })
    if order_items:
        new_id = len(orders) + 1
        orders.append({
            "id": new_id,
            "items": order_items,
            "total": total,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed": False
        })
    return redirect(url_for('index'))

@app.route('/admin')
@requires_auth
def admin():
    today = datetime.now().strftime("%Y-%m-%d")
    today_total = sum(order["total"] for order in orders if order["timestamp"].startswith(today))
    return render_template('admin.html', orders=orders, today_total=today_total)

@app.route('/mark_completed/<int:order_id>', methods=['POST'])
@requires_auth
def mark_completed(order_id):
    for order in orders:
        if order.get("id") == order_id:
            order["completed"] = True
            break
    return redirect(url_for('admin'))

@app.route('/delete_order/<int:order_id>', methods=['POST'])
@requires_auth
def delete_order(order_id):
    global orders
    orders = [order for order in orders if order.get("id") != order_id]
    return redirect(url_for('admin'))

@app.route('/clear_orders', methods=['POST'])
@requires_auth
def clear_orders():
    orders.clear()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
