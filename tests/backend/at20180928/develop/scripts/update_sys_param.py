from genesis_blockchain_api_client.backend.at20180928.develop.scripts.update_sys_params import (
    get_update_sys_param_args,
    update_sys_param,
)

if __name__ == '__main__':
    args = get_update_sys_param_args()
    update_sys_param(args.api_url, args.priv_key, args.name, args.value)
