import json
import urllib
import os
import argparse

from genesis_blockchain_api_client.utils import is_number

from genesis_blockchain_tools.contract import Contract
from genesis_blockchain_tools.crypto.genesis import public_key_to_address
from genesis_blockchain_tools.crypto.backend import (
    import_crypto_by_backend,
)

from genesis_blockchain_api_client.backend.at20180928.develop.calls import (
    get_uid, login, new_users as _new_users
)

from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

crypto = import_crypto_by_backend('cryptography')

backend_version = get_latest_version()
for option_name, option_value in version_to_options(backend_version).items():
    globals()[option_name] = option_value

def new_users(url, priv_key, keys_data,
              use_signtest=use_signtest, crypto_backend=crypto,
              use_login_prefix=use_login_prefix,
              pub_key_fmt=pub_key_fmt):
    uid, uid_token = get_uid(url)
    l_result = login(url,
                     priv_key, uid, uid_token,
                     sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)

    _new_users(url, priv_key, l_result['token'], keys_data,
               ecosystem_id=1, verify_cert=True, wait_tx=True,
               timeout_secs=20, max_tries=20, gap_secs=1)

def get_new_users_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--priv-key',
                        help='Private Key'),
    parser.add_argument('--api-url',
                        help='Backend API URL')
    parser.add_argument('--pub-key', action='append', nargs=1,
                        help='Public Key')
    parser.add_argument('--amount', action='append', nargs=1,
                        help='Amount')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('--no-debug', dest='debug', action='store_false',
                        help='Run in non-debug mode')
    parser.set_defaults(debug=False)
    args = parser.parse_args()
    params = {}
    if (hasattr(args, 'pub_key') and hasattr(args, 'amount') \
            and len(args.pub_key) == len(args.amount)) \
            or hasattr(args, 'pub_key'):
        i = 0
        for pub_key in args.pub_key:
            _pub_key = pub_key[0].rstrip()
            params[_pub_key] = {}
            if hasattr(args, 'amount'): 
                params[_pub_key]['amount'] = str(args.amount[i][0]).rstrip()
            i += 1
    return args.api_url, args.priv_key, params

if __name__ == '__main__':
    api_url, priv_key, params = get_update_keys_args()
    update_keys_raw(api_url, priv_key, params)
