import asyncio
from flask import Flask, request
from routes import home, products, offers, page_not_found
from utils import url_for_page
from config import config

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# add globals so they can be used in all templates  
app.jinja_env.globals["config"] = config
app.jinja_env.globals["url_for_page"] = url_for_page


@app.route("/")
@app.route("/home/")
def render_home():
    page = request.args.get("page", 0, type=int)
    return home(page)


@app.route("/<category>")
def render_products(category):
    category_id = request.args.get("id", type=int)
    page = request.args.get("page", 0, type=int)
    return products(loop, category_id, page)


@app.route("/<category>/<product>")
def render_offers(category, product):
    product_id = request.args.get("id", type=int)
    return offers(loop, product_id)


@app.errorhandler(404)
def render_page_not_found(error):
    return page_not_found()
