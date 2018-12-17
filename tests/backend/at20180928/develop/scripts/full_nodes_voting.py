from genesis_blockchain_api_client.backend.at20180928.develop.scripts.full_nodes_voting import (
    get_voting_conf_and_url_from_env,
    update_full_nodes_by_voting,
)

if __name__ == '__main__':
    conf, url = get_voting_conf_and_url_from_env()
    update_full_nodes_by_voting(conf, url)
