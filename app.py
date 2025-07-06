from flask import Flask, render_template, url_for
import qrcode
import os

app = Flask(__name__)

menu_items = [
    {"name": "漢堡", "price": 80, "image": "burger.jpg"},
    {"name": "炸雞", "price": 100, "image": "chicken.jpg"},
    {"name": "珍奶", "price": 60, "image": "milktea.jpg"},
]

# 🟡 固定網址
FIXED_SITE_URL = "https://orderapp-97th.onrender.com"

def generate_qrcode():
    img = qrcode.make(FIXED_SITE_URL)
    save_path = os.path.join(app.static_folder, "qrcode.png")
    if not os.path.exists(save_path):  # 如果還沒產生就建立一次
        img.save(save_path)

# 🟢 啟動時只產生一次
generate_qrcode()

@app.route("/")
def index():
    return render_template("index.html", menu=menu_items)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
