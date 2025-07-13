from flask import Flask, render_template, request, redirect, url_for, Response
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)

USERNAME = 'admin'
PASSWORD = '1234'

# 餐點資料
menu = [
    {"name": "漢堡", "price": 80, "image": "burger.jpg"},
    {"name": "炸雞", "price": 100, "image": "chicken.jpg"},
    {"name": "珍奶", "price": 60, "image": "milktea.jpg"}
]

orders = []

# 權限驗證
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

# 首頁
@app.route('/')
def index():
    return render_template('index.html', menu=menu)

# 提交訂單
@app.route('/submit_order', methods=['POST'])
def submit_order():
    order_items = []
    total = 0
    for item in menu:
        qty = int(request.form.get(f'quantity_{item["name"]}', 0))
        if qty > 0:
            subtotal = item['price'] * qty
            total += subtotal
            order_items.append({
                "name": item['name'],
                "price": item['price'],
                "quantity": qty,
                "done": False
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
        return redirect(url_for('success', order_id=new_id))
    return redirect(url_for('index'))

# 成功頁面（訂單編號回饋）
@app.route('/success')
def success():
    order_id = request.args.get('order_id', type=int)
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return redirect(url_for('index'))
    return render_template('success.html', order=order)

# 訂單狀態頁面（自動跳轉顧客查詢）
@app.route('/order_status')
def order_status():
    order_id = request.args.get('order_id', type=int)
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return redirect(url_for('index'))
    return render_template('order_status.html', order=order)

# 後台管理
@app.route('/admin')
@requires_auth
def admin():
    today = datetime.now().strftime("%Y-%m-%d")
    today_orders = [o for o in orders if o["timestamp"].startswith(today)]
    today_total = sum(o["total"] for o in today_orders)
    return render_template('admin.html', orders=orders, today_total=today_total)

# 單筆訂單完成
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

# 單一品項完成
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

# 刪除訂單
@app.route('/delete_order/<int:order_id>', methods=['POST'])
@requires_auth
def delete_order(order_id):
    global orders
    orders = [o for o in orders if o["id"] != order_id]
    return redirect(url_for('admin'))

# 清除所有訂單
@app.route('/clear_orders', methods=['POST'])
@requires_auth
def clear_orders():
    orders.clear()
    return redirect(url_for('admin'))

# 啟動應用
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
