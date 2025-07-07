from flask import Flask, render_template, request, redirect, url_for, Response
import os

app = Flask(__name__)
orders = []  # 儲存顧客訂單

# 餐點資料
menu_items = [
    {"name": "漢堡", "price": 80, "image": "burger.jpg"},
    {"name": "炸雞", "price": 100, "image": "chicken.jpg"},
    {"name": "珍奶", "price": 60, "image": "milktea.jpg"},
]

# 首頁顯示餐點
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", menu=menu_items)

# 接收點餐 POST 資料
@app.route("/order", methods=["POST"])
def order():
    selected_items = request.form.getlist("item")
    if selected_items:
        orders.append(selected_items)
    return redirect(url_for("index"))

# 管理者查看訂單
@app.route("/admin")
def admin():
    auth = request.authorization
    if not auth or auth.username != 'admin' or auth.password != '1234':
        return Response("無權限存取", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    return render_template("admin.html", orders=orders)

# 運行 Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
