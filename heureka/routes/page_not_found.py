from flask import render_template


def page_not_found():
    """Render page not found template.

    Returns:
        render_template function and error code
    """
    return render_template("page_not_found.html", title="Page not found"), 404
