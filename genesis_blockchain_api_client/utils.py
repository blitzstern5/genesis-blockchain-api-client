import re
import requests
import six
from requests_toolbelt.utils import dump

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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_string(s):
    return isinstance(s, six.string_types)

def is_bytes(s):
    return type(s) == bytes

def is_hash_string(s, min_len=32, max_len=512, ignore_case=True):
    if not is_string(s):
        return False
    if not len(s) >= min_len:
        return False
    if not len(s) <= max_len:
        return False
    flags = 0
    if ignore_case:
        flags |= re.IGNORECASE
    pattern = re.compile("^[a-z0-9]+$", flags=flags)
    return bool(pattern.match(s))

