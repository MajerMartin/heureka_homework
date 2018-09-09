import sys
sys.path.append("..")

from flask import render_template
from api import get_product, get_category, get_offers
from utils import clean_string

def offers(product_id):
    # download single product info
    product = get_product(product_id)

    # download single category info
    category = get_category(product["categoryId"])
    category["normalized_title"] = clean_string(category["title"])

    # download offers
    offers = get_offers(product_id)

    # aggregate offers
    img_urls = []
    description = None
    eshops = []

    for offer in offers:
        if offer.get("img_url"):
            img_urls.append(offer["img_url"])
        if not description and offer.get("description"):
            description = offer["description"]
        eshops.append({
            "url": offer["url"],
            "price": offer["price"],
            "title": offer["title"]
        })

    # sort offers by price
    eshops = sorted(eshops, key=lambda dct: dct["price"]) 

    return render_template("offers.html", title=product["title"],
                           category=category, img_urls=img_urls,
                           description=description, eshops=eshops)