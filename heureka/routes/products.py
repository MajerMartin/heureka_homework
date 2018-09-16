import sys

sys.path.append("..")

import asyncio
from flask import render_template
from api import get_categories, get_products, get_offers_async, get_products_count
from utils import clean_string
from config import config
from Pagination import Pagination


def get_products_statistics(loop, products):
    """Enrich products with additional statistics from offers.

    Args:
        loop (asyncio.unix_events._UnixSelectorEventLoop): asyncio event loop
        products (list): products of currently selected category

    Returns:
        list: products with additional statistics

    """
    description_placeholder = config["placeholders"]["description"]
    img_url_placeholder = config["placeholders"]["img_url"]

    # collect offers for all products asynchronously
    futures = [get_offers_async(product["productId"]) for product in products]
    all_offers = loop.run_until_complete(asyncio.gather(*futures))

    for product, offers in zip(products, all_offers):
        product["normalized_title"] = clean_string(product["title"])
        product["min_price"] = sys.maxsize
        product["max_price"] = 0
        product["description"] = description_placeholder
        product["img_url"] = img_url_placeholder

        for offer in offers:
            product["min_price"] = min(product["min_price"], offer["price"])
            product["max_price"] = max(product["max_price"], offer["price"])

            if product["description"] == description_placeholder and offer.get("description"):
                product["description"] = offer["description"]

            if product["img_url"] == img_url_placeholder and offer.get("img_url"):
                product["img_url"] = offer["img_url"]

    return products


def products(loop, category_id, page):
    """Render products template.

    Args:
        loop (asyncio.unix_events._UnixSelectorEventLoop): asyncio event loop
        category_id (int): id of currently selected category
        page (int): current pagination page

    Returns:
        render_template function

    """
    products_per_page = config["products"]["pagination"]["per_page"]

    # set asyncio loop for current module
    asyncio.set_event_loop(loop)

    # collect list of categories for left menu
    categories = get_categories()

    # collect one page of products for selected category
    offset = page * products_per_page

    products = get_products(category_id, offset, products_per_page)
    products = get_products_statistics(loop, products)

    # get total products count for pagination
    products_count = get_products_count(category_id)

    # set pagination to correct page
    pagination = Pagination(
        products_per_page,
        config["products"]["pagination"]["truncation_limit"],
        left_edge=config["products"]["pagination"]["left_edge"],
        right_edge=config["products"]["pagination"]["right_edge"],
        left_current=config["products"]["pagination"]["left_current"],
        right_current=config["products"]["pagination"]["right_current"]
    )

    pagination.set_current(page, products_count)

    return render_template("products.html", title="Products", categories=categories, products=products,
                           pagination=pagination, category_id=category_id)
