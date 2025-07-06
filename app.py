from flask import Flask, render_template, url_for
import qrcode
import os

app = Flask(__name__)

menu_items = [
    {"name": "漢堡", "price": 80, "image": "burger.jpg"},
    {"name": "炸雞", "price": 100, "image": "chicken.jpg"},
    {"name": "珍奶", "price": 60, "image": "milktea.jpg"}
]

def generate_qrcode():
    site_url = "https://orderapp-97th.onrender.com/"
    img = qrcode.make(site_url)
    save_path = os.path.join(app.static_folder, "qrcode.png")
    if not os.path.exists(save_path):  # ✅ 若不存在才生成
        img.save(save_path)

@app.route("/")
def index():
    generate_qrcode()  # ✅ 進入首頁時先產生 QR Code
    return render_template("index.html", menu=menu_items)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
