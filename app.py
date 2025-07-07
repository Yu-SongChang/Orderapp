from flask import Flask, render_template, request, redirect, url_for, Response

app = Flask(__name__)

# 餐點選單資料
menu_items = [
    {"name": "漢堡", "price": 80, "image": "burger.jpg"},
    {"name": "炸雞", "price": 100, "image": "chicken.jpg"},
    {"name": "珍奶", "price": 60, "image": "milktea.jpg"},
]

# 訂單資料儲存區
orders = []

# 首頁（點餐畫面）
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", menu=menu_items)

# 顧客送出訂單
@app.route("/submit_order", methods=["POST"])
def submit_order():
    order = []
    for item in menu_items:
        qty = int(request.form.get(f"quantity_{item['name']}", 0))
        if qty > 0:
            order.append({"name": item["name"], "quantity": qty})
    if order:
        orders.append(order)
    return redirect(url_for("index"))

# 簡單帳號密碼驗證
def check_auth(username, password):
    return username == "admin" and password == "1234"

def authenticate():
    return Response(
        "請輸入帳號密碼才能存取後台", 401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )

# 管理者後台
@app.route("/admin")
def admin():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    return render_template("admin.html", orders=orders)

# 啟動應用程式
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
