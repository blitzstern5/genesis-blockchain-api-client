from genesis_blockchain_api_client.backend.at20180928.develop.scripts.new_users import (
    get_new_users_args, new_users,
)

if __name__ == '__main__':
    api_url, priv_key, params = get_new_users_args()
    new_users(api_url, priv_key, params)
