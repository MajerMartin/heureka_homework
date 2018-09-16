import re
import json
import aiohttp
from flask import abort, url_for, request
from unidecode import unidecode
from urllib.parse import quote
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def get_response(query):
    """Get response to API request.

    Note: Query must start with '/'.

    Args:
        query (str): API request query
    Returns:
        dict: data from API

    """
    base_url = "http://python-servers-vtnovk529892.codeanyapp.com:5000{}"
    request = Request(base_url.format(query))

    try:
        response = urlopen(request).read()
        return json.loads(response)
    except HTTPError:
        abort(404)


async def get_response_async(query):
    """Asynchronously get response to API request.

    Note: Query must start with '/'.

    Args:
        query (str): API request query
    Returns:
        dict: data from API

    """
    base_url = "http://python-servers-vtnovk529892.codeanyapp.com:5000{}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url.format(query)) as response:
                return await response.json()
    except aiohttp.client_exceptions.ServerDisconnectedError:
        abort(404)


def clean_string(text):
    """Clean and normalize text

    Args:
        text (str): text to clean

    Returns:
        str: cleaned text

    """
    # convert to lowercase and replace spaces
    text = re.sub(r"\s+", "-", text.lower(), flags=re.UNICODE)

    # replace accents
    text = unidecode(text)

    # normalize rest of the string
    return quote(text)


def url_for_page(page, kwargs={}):
    """Create url for target endpoint with page parameter.

    Args:
        page (int): page number 
        kwargs (dict, optional): other query parameters

    Returns:
        url with page parameter
    
    """
    args = request.view_args.copy()
    args["page"] = page
    all_args = {**args, **kwargs}
    return url_for(request.endpoint, **all_args)
