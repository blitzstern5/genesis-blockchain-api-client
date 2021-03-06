import json
import os
import argparse

from genesis_blockchain_api_client.utils import is_number

from genesis_blockchain_tools.contract import Contract
from genesis_blockchain_tools.crypto.backend import (
    import_crypto_by_backend,
)

from genesis_blockchain_api_client.backend.at20180928.develop.calls import (
    get_uid, login, update_sys_param as _update_sys_param,
    update_sys_params as _update_sys_params, url_to_address,
)

from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

crypto = import_crypto_by_backend('cryptography')

backend_version = get_latest_version()
for option_name, option_value in version_to_options(backend_version).items():
    globals()[option_name] = option_value

def update_sys_param(url, priv_key, name, value,
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

    _update_sys_param(url, priv_key, l_result['token'],
                      name, value, ecosystem_id=1,
                      verify_cert=True, wait_tx=True, timeout_secs=timeout_secs,
                      max_tries=max_tries, gap_secs=1)

def get_update_full_nodes_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--call-priv-key', required=True,
                        help='Private Key to call full nodes update'),
    parser.add_argument('--call-api-url', required=True,
                        help='Backend API URL to call full nodes update')
    parser.add_argument('--node-api-url', action='append', nargs=1,
                        required=True, help='Node API URL"')
    parser.add_argument('--node-tcp-addr', action='append', nargs=1,
                        required=True, help='Node TCP address')
    parser.add_argument('--node-key-id', action='append', nargs=1,
                        required=True, help='Node key ID')
    parser.add_argument('--node-pub-key', action='append', nargs=1,
                        required=True, help='Node public key')
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
    params = []
    if hasattr(args, 'node_api_url') and hasattr(args, 'node_tcp_addr') \
            and hasattr(args, 'node_key_id') and hasattr(args, 'node_pub_key') \
            and args.node_api_url and args.node_tcp_addr \
            and args.node_key_id and args.node_pub_key \
            and len(args.node_api_url) == len(args.node_tcp_addr) \
            and len(args.node_api_url) == len(args.node_key_id) \
            and len(args.node_key_id) == len(args.node_pub_key):
        i = 0
        for node_api_url in args.node_api_url:
            params.append({
                'api_address': url_to_address(node_api_url[0]),
                'tcp_address': args.node_tcp_addr[i][0],
                'key_id': args.node_key_id[i][0],
                'public_key': args.node_pub_key[i][0],
            })
            i += 1
    return args.call_api_url, args.call_priv_key, json.dumps(params), \
           args.timeout_secs, args.max_tries

if __name__ == '__main__':
    api_url, priv_key, full_nodes_str, timeout_secs, max_tries \
            = get_update_full_nodes_args()
    update_sys_param(api_url, priv_key, 'full_nodes', full_nodes_str, timeout_secs=timeout_secs, max_tries=max_tries)

