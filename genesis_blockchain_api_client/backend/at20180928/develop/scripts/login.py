import json
import urllib
import os
import argparse

from genesis_blockchain_api_client.utils import is_number

from genesis_blockchain_tools.contract import Contract
from genesis_blockchain_tools.crypto.backend import (
    import_crypto_by_backend,
)

from genesis_blockchain_api_client.backend.at20180928.develop.calls import (
    get_uid, login as _login
)

from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

crypto_backend = import_crypto_by_backend('cryptography')

backend_version = get_latest_version()
for option_name, option_value in version_to_options(backend_version).items():
    globals()[option_name] = option_value

def login(url, priv_key, ecosystem_id=1, verify_cert=True):
    uid, uid_token = get_uid(url)
    l_result = _login(url,
                     priv_key, uid, uid_token,
                     sign_fmt=sign_fmt,
                     use_signtest=use_signtest,
                     crypto_backend=crypto_backend,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)
    return l_result

def get_login_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--priv-key', required=True, help='Private Key'),
    parser.add_argument('--api-url', required=True, help='Backend API URL')
    parser.add_argument('--ecosystem', default=1, help='Ecosystem ID')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('--no-debug', dest='debug', action='store_false',
                        help='Run in non-debug mode')
    parser.set_defaults(debug=False)
    args = parser.parse_args()
    params = {}
    if hasattr(args, 'name') and hasattr(args, 'value') \
        and args.name and args.value \
        and len(args.name) == len(args.value):
        i = 0
        for name in args.name:
            params[name[0]] = args.value[i][0]
            i += 1
    return args.api_url, args.priv_key, args.ecosystem

if __name__ == '__main__':
    pass
    api_url, priv_key, ecosystem_id = get_login_args()
    print("api_url: %s priv_key: %s" % (api_url, priv_key))
    result = login(api_url, priv_key, ecosystem_id=ecosystem_id)
    print("token: %s" % result['token'])
