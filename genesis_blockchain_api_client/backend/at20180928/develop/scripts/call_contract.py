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
    get_uid, login, call_contract as _call_contract,
)

from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

crypto = import_crypto_by_backend('cryptography')

backend_version = get_latest_version()
for option_name, option_value in version_to_options(backend_version).items():
    globals()[option_name] = option_value

def call_contract(url, priv_key, name, params, ecosystem_id=1,
                  timeout_secs=40, max_tries=40, gap_secs=1,
                  verify_cert=True):
    uid, uid_token = get_uid(url)
    l_result = login(url,
                     priv_key, uid, uid_token,
                     sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)

    _call_contract(url, priv_key, l_result['token'], name, params,
                   ecosystem_id=ecosystem_id,
                   verify_cert=verify_cert, wait_tx=True,
                   timeout_secs=timeout_secs, max_tries=max_tries,
                   gap_secs=gap_secs)

def get_call_contract_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--priv-key', required=True, help='Private Key'),
    parser.add_argument('--api-url', required=True, help='Backend API URL')
    parser.add_argument('--contract', required=True, help='Contract Name')
    parser.add_argument('--ecosystem', default=1, help='Ecosystem ID')
    parser.add_argument('-n', '--name', action='append', nargs=1,
                        help='Parameter Name')
    parser.add_argument('-v', '--value', action='append', nargs=1,
                        help='Parameter Value')
    parser.add_argument('--timeout-secs', default=40, type=int,
                        help='Timeout in seconds')
    parser.add_argument('--max-tries', default=40, type=int,
                        help='Maximum numbers of tries')
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
    return args.api_url, args.priv_key, args.contract, params, \
           args.ecosystem, args.timeout_secs, args.max_tries

if __name__ == '__main__':
    api_url, priv_key, contract, params, ecosystem_id, timeout_secs, max_tries \
            = get_call_contract_args()
    call_contract(api_url, priv_key, contract, params,
                  ecosystem_id=ecosystem_id,
                  timeout_secs=timeout_secs, max_tries=max_tries)

