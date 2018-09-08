import re
import json
from flask import abort
from unidecode import unidecode
from urllib.parse import quote
from urllib.error import HTTPError
from urllib.request import Request, urlopen


# TODO: used everywhere, cache this
def get_response(query):
    base_url = "http://python-servers-vtnovk529892.codeanyapp.com:5000{}"
    request = Request(base_url.format(query))
    
    try:
        response = urlopen(request).read()
        return json.loads(response)
    # TODO: what about other exceptions?
    except HTTPError:
        abort(404)

def clean_string(text):
    # convert to lowercase and replace spaces
    text = re.sub(r"\s+", "-", text.lower(), flags=re.UNICODE)
    
    # replace accents
    text = unidecode(text)

    # normalize rest of the string
    return quote(text)

# TODO: write test for this one
def build_url(*args, **kwargs):
    base = "/".join(args)
    params = "&".join(["{}={}".format(key, value) for key, value in kwargs.items()])

    return "{}?{}".format(base, params)
    

