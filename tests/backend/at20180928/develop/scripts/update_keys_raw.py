from genesis_blockchain_api_client.backend.at20180928.develop.scripts.update_keys_raw import (
    get_update_keys_args,
    update_keys_raw,
)

if __name__ == '__main__':
    api_url, priv_key, params = get_update_keys_args()
    update_keys_raw(api_url, priv_key, params)
