import sys

sys.path.append("..")

from flask import render_template
from api import get_categories
from config import config
from Pagination import Pagination


def home(page):
    """Render home template.

    Args:
        page (int): current pagination page

    Returns:
        render_template function

    """
    categories = get_categories()
    categories_per_page = config["categories"]["pagination"]["per_page"]

    # set pagination to correct page    
    pagination = Pagination(
        categories_per_page,
        config["categories"]["pagination"]["truncation_limit"],
        left_edge=config["categories"]["pagination"]["left_edge"],
        right_edge=config["categories"]["pagination"]["right_edge"],
        left_current=config["categories"]["pagination"]["left_current"],
        right_current=config["categories"]["pagination"]["right_current"]
    )

    pagination.set_current(page, len(categories))

    # select categories for given page
    lower_bound = page * categories_per_page
    upper_bound = (page + 1) * categories_per_page

    tile_ids = list(categories.keys())[lower_bound:upper_bound]
    tile_categories = {id: categories[id] for id in tile_ids}

    return render_template("home.html", title="Categories", pagination=pagination, categories=categories,
                           tile_categories=tile_categories)
