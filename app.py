from flask import Flask, render_template, request, redirect, url_for, Response
import os
from functools import wraps

app = Flask(__name__)
orders = []

menu_items = [
    {"name": "漢堡", "price": 80, "image": "burger.jpg"},
    {"name": "炸雞", "price": 100, "image": "chicken.jpg"},
    {"name": "珍奶", "price": 60, "image": "milktea.jpg"},
]

# 🔐 建立登入驗證裝飾器
def check_auth(username, password):
    return username == 'admin' and password == '1234'

def authenticate():
    return Response(
        '請輸入帳號密碼', 401,
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

@app.route("/")
def index():
    return render_template("index.html", menu=menu_items)

@app.route("/order", methods=["POST"])
def order():
    selected_items = request.form.getlist("item")
    if selected_items:
        orders.append(selected_items)
    return redirect(url_for("index"))

# ✅ 加入驗證的後台路由
@app.route("/admin")
@requires_auth
def admin():
    return render_template("admin.html", orders=orders)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
