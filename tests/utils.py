import six
import re
import os

from genesis_blockchain_tools import crypto

class Error(Exception): pass
class PrivKeyIsNotSetError(Error):
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            m = "type(priv_key): '%s', priv_key: %s" % (type(args[0]), args[0])
            args = (m,) + args[1:]
        super(PrivKeyIsNotSetError, self).__init__(*args, **kwargs)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_string(s):
    return isinstance(s, six.string_types)

def is_hash_string(s, min_len=32, max_len=512, ignore_case=True):
    assert is_string(s)
    assert len(s) >= min_len
    assert len(s) <= max_len
    flags = 0
    if ignore_case:
        flags |= re.IGNORECASE
    pattern = re.compile("^[a-z0-9]+$", flags=flags)
    return pattern.match(s)

def save_keypair_as(priv_key, pub_key, crypto, good_or_bad="bad"):
    basedir = os.path.abspath(os.path.dirname(__file__))
    if good_or_bad not in ['bad', 'good']:
        return
    path = os.path.join(basedir, crypto.backend_name + '-keys-' + good_or_bad \
                        + ".log")
    with open(path, "a") as keys_log:
        keys_log.write("%s %s\n" % (priv_key, pub_key))

def save_signature_as(priv_key, pub_key, crypto, good_or_bad="bad"):
    basedir = os.path.abspath(os.path.dirname(__file__))
    if good_or_bad not in ['bad', 'good']:
        return
    path = os.path.join(basedir, crypto.backend_name + '-signatures-' \
                        + good_or_bad + ".log")
    with open(path, "a") as keys_log:
        keys_log.write("%s %s\n" % (priv_key, pub_key))
