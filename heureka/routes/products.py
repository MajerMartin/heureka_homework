import sys
sys.path.append("..")

from flask import render_template
from math import ceil
from api import get_categories, get_products, get_offers, get_products_count
from utils import clean_string, build_url

def get_products_statistics(products):
    for product in products:
        product["normalized_title"] = clean_string(product["title"])
        product["min_price"] = 10e10
        product["max_price"] = 0
        product["description"] = None
        product["img_url"] = None

        offers = get_offers(product["productId"])

        for offer in offers:
            product["min_price"] = min(product["min_price"], offer["price"])
            product["max_price"] = max(product["max_price"], offer["price"])

            if not product["description"] and offer.get("description"):
                product["desc"] = offer["description"]

            if not product["img_url"] and offer.get("img_url"):
                product["img_url"] = offer["img_url"]

    # TODO: solve missing desc and img in template?
    return products
    
def products(category_id, page, products_per_page=5):
    # recollect list of categories for left menu
    categories = get_categories()

    # collect one page of products for selected category
    offset = page * products_per_page
    
    products = get_products(category_id, offset, products_per_page)
    products = get_products_statistics(products)

    # get total products count for pagination
    products_count = get_products_count(category_id)
    pages_count = ceil(products_count / products_per_page)
    
    # TODO: async load next page - user is more likely to visit it
    
    return render_template("products.html", title="Products",
                           categories=categories, products=products,
                           page=page, pages_count=pages_count,
                           category_id=category_id, build_url=build_url)