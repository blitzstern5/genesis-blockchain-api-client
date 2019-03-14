from genesis_blockchain_api_client.backend.at20180928.develop.scripts.call_contract import (
    get_call_contract_args, call_contract,
)

if __name__ == '__main__':
    api_url, priv_key, contract, params, ecosystem_id, timeout_secs, max_tries \
            = get_call_contract_args()
    call_contract(api_url, priv_key, contract, params,
                  ecosystem_id=ecosystem_id,
                  timeout_secs=timeout_secs, max_tries=max_tries)
