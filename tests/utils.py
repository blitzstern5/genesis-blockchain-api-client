import six
import os

from genesis_blockchain_tools import crypto

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_string(s):
    return isinstance(s, six.string_types)

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
