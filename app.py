from flask import Flask, render_template, request, redirect, url_for, Response
import os

app = Flask(__name__)

menu_items = [
    {"name": "漢堡", "price": 80, "image": "burger.jpg"},
    {"name": "炸雞", "price": 100, "image": "chicken.jpg"},
    {"name": "珍奶", "price": 60, "image": "milktea.jpg"}
]

orders = []

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", menu=menu_items)

@app.route("/submit_order", methods=["POST"])
def submit_order():
    order = []
    for item in menu_items:
        qty = int(request.form.get(f"quantity_{item['name']}", 0))
        if qty > 0:
            order.append({"name": item['name'], "quantity": qty})
    if order:
        orders.append(order)
    return redirect(url_for('index'))

# 管理員介面（保留簡單版）
@app.route("/admin")
def admin():
    return render_template("admin.html", orders=orders)
