from genesis_blockchain_api_client.backend.at20180928.develop.scripts.import_dapps import (
    get_import_dapp_from_file_args,
    import_dapp_from_file,
)

if __name__ == '__main__':
    api_url, priv_key, path, timeout_secs, max_tries  = get_import_dapp_from_file_args()
    import_dapp_from_file(api_url, priv_key, path, timeout_secs=timeout_secs,
                          max_tries=max_tries)
