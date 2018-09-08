from json import load
from flask import Flask, request
from routes import home, products, offers, page_not_found

app = Flask(__name__)

with open("config.json", "r") as fr:
    config = load(fr)

@app.route("/")
@app.route("/home/")
def render_home():
    page = request.args.get("page", 0, type=int)
    return home(page, categories_per_page=config["categories_per_page"])

@app.route("/<category>")
def render_products(category):
    category_id = request.args.get("id", type=int)
    page = request.args.get("page", 0, type=int)
    return products(category_id, page, products_per_page=config["products_per_page"])

@app.route("/<category>/<product>")
def render_offers(category, product):
    product_id = request.args.get("id", type=int)
    return offers(product_id)

@app.errorhandler(404)
def render_page_not_found(error):
    return page_not_found()