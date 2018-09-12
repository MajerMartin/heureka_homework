import sys
sys.path.append("..")

from flask import render_template
from api import get_product, get_category, get_offers
from utils import clean_string
from config import config

def offers(product_id):
    description_placeholder = config["placeholders"]["description"]

    # download single product info
    product = get_product(product_id)

    # download single category info
    category = get_category(product["categoryId"])
    category["normalized_title"] = clean_string(category["title"])

    # download offers
    offers = get_offers(product_id)

    # aggregate offers
    img_urls = []
    description = description_placeholder
    eshops = []

    for offer in offers:
        if offer.get("img_url"):
            img_urls.append(offer["img_url"])
        if description == description_placeholder and offer.get("description"):
            description = offer["description"]
        eshops.append({
            "url": offer["url"],
            "price": offer["price"],
            "title": offer["title"]
        })

    # sort offers by price
    eshops = sorted(eshops, key=lambda dct: dct["price"]) 

    # just for this homework to remove duplicates
    img_urls = list(set(img_urls))

    return render_template("offers.html", title=product["title"],
                           category=category, img_urls=img_urls,
                           description=description, eshops=eshops)