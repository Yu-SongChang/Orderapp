# 匯入必要模組
from flask import Flask, render_template
import qrcode
import os

app = Flask(__name__)

# 商品資料
menu_items = [
    {"name": "漢堡", "price": 80, "image": "burger.jpg"},
    {"name": "炸雞", "price": 100, "image": "chicken.jpg"},
    {"name": "珍奶", "price": 60, "image": "milktea.jpg"}
]

# 固定網址：產生 QR Code 會指向這個 Render 網站
FIXED_SITE_URL = "https://orderapp-97th.onrender.com/"

# 產生 QR Code
def generate_qrcode():
    img = qrcode.make(FIXED_SITE_URL)
    save_path = os.path.join(app.static_folder, "qrcode.png")
    if not os.path.exists(save_path):  # 若檔案還沒存在就建立
        img.save(save_path)

# 程式一啟動就產生 QR Code
generate_qrcode()

# 首頁路由
@app.route("/")
def index():
    return render_template("index.html", menu=menu_items)

# 啟動伺服器（Render 會使用的埠號）
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
