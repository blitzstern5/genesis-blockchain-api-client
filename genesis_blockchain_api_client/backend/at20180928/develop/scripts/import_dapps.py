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
    get_uid, login, upload_import_data_from_file, fetch_imported_data,
    import_data,
)

from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

crypto = import_crypto_by_backend('cryptography')

backend_version = get_latest_version()
for option_name, option_value in version_to_options(backend_version).items():
    globals()[option_name] = option_value

def import_dapp_from_file(url, priv_key, path,
                    use_signtest=use_signtest, crypto_backend=crypto,
                    use_login_prefix=use_login_prefix,
                    pub_key_fmt=pub_key_fmt, timeout_secs=150,
                    max_tries=150):
    uid, uid_token = get_uid(url)
    l_result = login(url,
                     priv_key, uid, uid_token,
                     sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)

    print("Uploading data ...")
    upload_import_data_from_file(url, priv_key, l_result['token'], path,
                                 timeout_secs=timeout_secs,
                                 max_tries=max_tries)
    data = fetch_imported_data(url, priv_key, l_result['token'])
    print("Importing data ...")
    w_result = import_data(url, priv_key, l_result['token'], data,
                           verify_cert=True, timeout_secs=timeout_secs,
                           max_tries=max_tries)


def get_import_dapp_from_file_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--priv-key', required=True, help='Private Key'),
    parser.add_argument('--api-url', required=True, help='Backend API URL')
    parser.add_argument('--path', required=True, help='Path to DApp')
    parser.add_argument('--timeout-secs', default=150,
                        help='Timeout in seconds')
    parser.add_argument('--max-tries', default=150,
                        help='Maximum numbers of tries')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('--no-debug', dest='debug', action='store_false',
                        help='Run in non-debug mode')
    parser.set_defaults(debug=False)
    args = parser.parse_args()
    return args.api_url, args.priv_key, args.path, \
            int(args.timeout_secs), int(args.max_tries)

if __name__ == '__main__':
    api_url, priv_key, path, timeout_secs, max_tries = get_import_dapp_from_file_args()
    import_dapp_from_file(api_url, priv_key, path, timeout_secs=timeout_secs,
                          max_tries=max_tries)

