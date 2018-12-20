from genesis_blockchain_api_client.backend.at20180928.develop.scripts.update_sys_params import (
    get_update_full_nodes_args,
    update_sys_param,
)

if __name__ == '__main__':
    api_url, priv_key, full_nodes_str = get_update_full_nodes_args()
    update_sys_param(api_url, priv_key, full_nodes_str)
