import requests
from requests_toolbelt.utils import dump

def dump_resp(resp):
    if isinstance(resp, requests.Response):
        data = dump.dump_all(resp)
    return data.decode('utf-8')
