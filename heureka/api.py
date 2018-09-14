from sys import maxsize
from collections import OrderedDict
from utils import get_response, clean_string
from Cache import Cache
from config import config


@Cache(max_lifetime=600)
def get_categories():
    categories_list = get_response("/categories")

    # turn into dictionary for category ID lookup
    categories_dict = OrderedDict()

    for category in categories_list:
        key = category["categoryId"]
        categories_dict[key] = {
            "title": category["title"],
            "normalized_title": clean_string(category["title"])
        }

    return categories_dict


@Cache(max_lifetime=120)
def get_category(category_id):
    return get_response("/category/{}".format(category_id))


@Cache(max_size=2 * config["products"]["pagination"]["per_page"], max_lifetime=120, group_key="category_id")
def get_products(category_id, offset=0, limit=maxsize):
    return get_response("/products/{}/{}/{}".format(category_id, offset, limit))


@Cache(max_lifetime=120)
def get_products_count(category_id):
    return get_response("/products/{}/count/".format(category_id))["count"]


@Cache(max_lifetime=120)
def get_product(product_id):
    return get_response("/product/{}".format(product_id))


@Cache(max_lifetime=120)
def get_offers(product_id, offset=0, limit=maxsize):
    return get_response("/offers/{}/{}/{}".format(product_id, offset, limit))


@Cache(max_lifetime=120)
def get_offers_count(product_id):
    return get_response("/offers/{}/count/".format(product_id))["count"]


@Cache(max_lifetime=120)
def get_offer(offer_id):
    return get_response("/offer/{}".format(offer_id))
