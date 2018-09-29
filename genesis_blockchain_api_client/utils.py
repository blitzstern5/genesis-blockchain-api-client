import requests
from requests_toolbelt.utils import dump
import re

def dump_resp(resp):
    if isinstance(resp, requests.Response):
        data = dump.dump_all(resp)
    try:
        data = data.decode('utf-8')
    except UnicodeDecodeError:
        try:
            data = data.decode()
        except UnicodeDecodeError:
            pass
    return data

def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
