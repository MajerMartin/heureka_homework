import sys
sys.path.append("..")

from math import ceil
from flask import render_template
from api import get_categories
from utils import build_url

def home(page, categories_per_page=9):
    categories = get_categories()
    
    pages_count = ceil(len(categories) / categories_per_page)
    
    lower_bound = page * categories_per_page
    upper_bound = (page + 1) * categories_per_page

    # TODO: do this better?
    tile_ids = list(categories.keys())[lower_bound:upper_bound]
    tile_categories = {id: categories[id] for id in tile_ids}
    
    return render_template("home.html", title="Categories",
                           page=page, pages_count=pages_count,
                           categories=categories,
                           tile_categories=tile_categories,
                           build_url=build_url)