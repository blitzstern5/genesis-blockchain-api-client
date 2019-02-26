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
    get_uid, login, update_keys_raw as _update_keys_raw,
)

from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

crypto = import_crypto_by_backend('cryptography')

backend_version = get_latest_version()
for option_name, option_value in version_to_options(backend_version).items():
    globals()[option_name] = option_value

def update_keys_raw(url, priv_key, keys_data,
                    use_signtest=use_signtest, crypto_backend=crypto,
                    use_login_prefix=use_login_prefix,
                    pub_key_fmt=pub_key_fmt, timeout_secs=40,
                    max_tries=40):
    uid, uid_token = get_uid(url)
    l_result = login(url,
                     priv_key, uid, uid_token,
                     sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)

    _update_keys_raw(url, priv_key, l_result['token'], keys_data,
                     ecosystem_id=1, verify_cert=True, wait_tx=True,
                     timeout_secs=timeout_secs, max_tries=max_tries,
                     gap_secs=1)

def get_update_keys_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--priv-key', required=True, help='Private Key'),
    parser.add_argument('--api-url', required=True, help='Backend API URL')
    parser.add_argument('--key-id', action='append', nargs=1, required=True,
                        help='Key ID')
    parser.add_argument('--pub-key', action='append', nargs=1, required=True,
                        help='Public Key')
    parser.add_argument('--amount', action='append', nargs=1, help='Amount')
    parser.add_argument('--timeout-secs', default=40, help='Timeout in seconds')
    parser.add_argument('--max-tries', default=40,
                        help='Maximum numbers of tries')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('--no-debug', dest='debug', action='store_false',
                        help='Run in non-debug mode')
    parser.set_defaults(debug=False)
    args = parser.parse_args()
    params = {}
    if hasattr(args, 'key_id') and hasattr(args, 'pub_key') \
            and hasattr(args, 'amount') \
            and len(args.key_id) == len(args.pub_key) \
            and len(args.key_id) == len(args.amount):
        i = 0
        for key_id in args.key_id:
            params[key_id[0]] = {'pub_key': args.pub_key[i][0],
                                 'amount': args.amount[i][0]}
            i += 1
    return args.api_url, args.priv_key, params, args.timeout_secs, \
           args.max_tries

if __name__ == '__main__':
    api_url, priv_key, params, timeout_secs, max_tries = get_update_keys_args()
    update_keys_raw(api_url, priv_key, params, timeout_secs=timeout_secs,
                    max_tries=max_tries)
