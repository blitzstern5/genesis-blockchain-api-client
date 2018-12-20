from genesis_blockchain_api_client.backend.at20180928.develop.scripts.update_sys_params import (
    get_update_sys_params_args,
    update_sys_params,
)

if __name__ == '__main__':
    api_url, priv_key, params = get_update_sys_params_args()
    print("api_url: %s priv_key: %s params: %s" % (api_url, priv_key, params))
    #update_sys_params(api_url, priv_key, params)
