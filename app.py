from flask import Flask, render_template, request, redirect, url_for, Response
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)

# 帳號密碼設定
USERNAME = 'admin'
PASSWORD = '1234'

# 餐點資料
menu = [
    {"name": "漢堡", "price": 80, "image": "burger.jpg"},
    {"name": "炸雞", "price": 100, "image": "chicken.jpg"},
    {"name": "珍奶", "price": 60, "image": "milktea.jpg"}
]

# 訂單紀錄
orders = []

# 權限驗證
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

# 首頁（點餐）
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', menu=menu, orders=orders)

# 提交訂單
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
        new_id = len(orders) + 1  # ✅ 訂單編號
        orders.append({
            "id": new_id,  # ✅ 編號
            "items": order_items,
            "total": total,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed": False
        })
    return redirect(url_for('index'))

# 後台頁面（需登入）
@app.route('/admin')
@requires_auth
def admin():
    return render_template('admin.html', orders=orders)

# 標記訂單為完成
@app.route('/mark_completed/<int:order_id>', methods=['POST'])
@requires_auth
def mark_completed(order_id):
    for order in orders:
        if order["id"] == order_id:
            order["completed"] = True
            break
    return redirect(url_for('admin'))

# 刪除單筆訂單
@app.route('/delete_order/<int:order_id>', methods=['POST'])
@requires_auth
def delete_order(order_id):
    global orders
    orders = [order for order in orders if order["id"] != order_id]
    return redirect(url_for('admin'))

# 清除全部訂單
@app.route('/clear_orders', methods=['POST'])
@requires_auth
def clear_orders():
    orders.clear()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
