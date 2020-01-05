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
    get_uid, login, update_sys_param as _update_sys_param,
    update_sys_params as _update_sys_params
)

from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

crypto_backend = import_crypto_by_backend('cryptography')

backend_version = get_latest_version()
for option_name, option_value in version_to_options(backend_version).items():
    globals()[option_name] = option_value

def update_sys_param(url, priv_key, name, value,
                     use_signtest=use_signtest,
                     crypto_backend=crypto_backend,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt, timeout_secs=40,
                     max_tries=40):
    uid, uid_token = get_uid(url)
    l_result = login(url,
                     priv_key, uid, uid_token,
                     sign_fmt=sign_fmt,
                     use_signtest=use_signtest,
                     crypto_backend=crypto_backend,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)

    _update_sys_param(url, priv_key, l_result['token'],
                      name, value, ecosystem_id=1,
                      verify_cert=True, wait_tx=True, timeout_secs=timeout_secs,
                      max_tries=max_tries, gap_secs=1)

def update_sys_params(url, priv_key, name_value_map,
                     use_signtest=use_signtest,
                     crypto_backend=crypto_backend,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt, timeout_secs=40,
                     max_tries=40):
    uid, uid_token = get_uid(url)
    l_result = login(url,
                     priv_key, uid, uid_token,
                     sign_fmt=sign_fmt,
                     use_signtest=use_signtest,
                     crypto_backend=crypto_backend,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)

    _update_sys_params(url, priv_key, l_result['token'],
                      name_value_map, ecosystem_id=1,
                      verify_cert=True, wait_tx=True, timeout_secs=timeout_secs,
                      max_tries=max_tries, gap_secs=1)


def get_update_sys_param_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--priv-key',
                        help='Private Key'),
    parser.add_argument('--api-url',
                        help='Backend API URL')
    parser.add_argument('-n', '--name',
                        help='System Parameter Name')
    parser.add_argument('-v', '--value',
                        help='System Parameter Value')
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
    return args

def get_update_sys_params_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--priv-key', required=True, help='Private Key'),
    parser.add_argument('--api-url', required=True, help='Backend API URL')
    parser.add_argument('-n', '--name', action='append', nargs=1,
                        required=True, help='System Parameter Name')
    parser.add_argument('-v', '--value', action='append', nargs=1,
                        required=True, help='System Parameter Value')
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
    return args.api_url, args.priv_key, params, args.timeout_secs, \
           args.max_tries

if __name__ == '__main__':
    api_url, priv_key, params, timeout_secs, max_tries \
            = get_update_sys_params_args()
    update_sys_params(api_url, priv_key, params, timeout_secs=timeout_secs,
                      max_tries=max_tries)
