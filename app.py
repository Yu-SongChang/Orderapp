from flask import Flask, render_template, request, redirect
import qrcode
import os

app = Flask(__name__)

# 固定網址
FIXED_SITE_URL = "https://orderapp-97th.onrender.com"

# 模擬菜單資料
menu_items = [
    {"name": "漢堡", "price": 80, "image": "burger.jpg"},
    {"name": "炸雞", "price": 100, "image": "chicken.jpg"},
    {"name": "珍奶", "price": 60, "image": "milktea.jpg"}
]

# 建立 QR Code（只產生一次）
def generate_qrcode():
    img = qrcode.make(FIXED_SITE_URL)
    save_path = os.path.join(app.static_folder, "qrcode.png")
    if not os.path.exists(save_path):
        img.save(save_path)

generate_qrcode()

# 儲存訂單列表
orders = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_items = request.form.getlist("item")
        if selected_items:
            order_text = ", ".join(selected_items)
            orders.append(order_text)
        return redirect("/")  # 避免重新整理重送資料
    return render_template("index.html", menu=menu_items)

@app.route("/admin")
def admin():
    return render_template("admin.html", all_orders=orders)

# 啟動伺服器
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
