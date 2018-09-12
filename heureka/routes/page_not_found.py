from flask import render_template

def page_not_found():
    return render_template("page_not_found.html", title="Page not found"), 404