import json
import urllib
import os
from collections import OrderedDict

from genesis_blockchain_api_client.utils import is_number

from genesis_blockchain_tools.contract import Contract
from genesis_blockchain_tools.crypto.genesis import public_key_to_address
from genesis_blockchain_tools.crypto.backend import (
    import_crypto_by_backend,
)

from genesis_blockchain_api_client.backend.at20180928.develop.calls import (
    GENESIS_COMMON_ROLE_ID, APLA_COMMON_ROLE_ID,
    GENESIS_ADMIN_ROLE_ID, APLA_ADMIN_ROLE_ID,
    GENESIS_CONSENSUS_ROLE_ID, APLA_CONSENSUS_ROLE_ID,
    get_uid, login, install_roles, install_voting_templates, assign_role,
    assign_apla_consensus_role, edit_app_param, edit_profile,
    add_node_by_voting, update_voting_status,
    accept_voting_decision,
)

from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

crypto = import_crypto_by_backend('cryptography')

backend_version = get_latest_version()
for option_name, option_value in version_to_options(backend_version).items():
    globals()[option_name] = option_value


class Error(Exception): pass

def get_var_from_env(node_ind, templates):
    assert is_number(node_ind)
    assert node_ind >= 1
    value = None
    for tmpl in templates:
        value = os.environ.get(tmpl % node_ind)
        if value is not None:
            break
    return value

def url_to_address(url):
    return urllib.parse.urlunparse(tuple(urllib.parse.urlparse(url))[:-4] + tuple((',' * 3).split(',')))

def get_vars_from_env(templates_map, max_node_ind, min_node_ind=1):
    data = OrderedDict()
    for node_ind in range(min_node_ind, max_node_ind + 1):
        for target, templates in templates_map.items():
            if node_ind not in data:
                data[node_ind] = {}
            data[node_ind][target] = get_var_from_env(node_ind, templates)
            if target == 'int_api_url':
                data[node_ind]['int_api_address'] = url_to_address(data[node_ind][target])
            if target == 'api_url':
                data[node_ind]['api_address'] = url_to_address(data[node_ind][target])
    return data

def update_full_nodes_by_voting(conf, url=None,
                                sign_fmt=sign_fmt,
                                use_signtest=use_signtest,
                                crypto_backend=crypto,
                                use_login_prefix=use_login_prefix,
                                pub_key_fmt=pub_key_fmt):
    """
    OrderedDict:
    conf = {
        1: {
            'priv_key': 'PRIV_KEY',
            'key_id': 'KEY_ID',
            'pub_key': 'PUB_KEY',
            'api_url': 'API_URL',
            'tcp_address': 'TCP_ADDRESS',
        },
        2: {
            'priv_key': 'PRIV_KEY',
            'key_id': 'KEY_ID',
            'pub_key': 'PUB_KEY',
            'api_url': 'API_URL',
            'tcp_address': 'TCP_ADDRESS',
        },
    }

    """

    first_node_ind = tuple(conf.items())[0][0]
    first_node_conf = tuple(conf.items())[0][1]
    other_node_inds = tuple(conf.keys())[1:]

    if not url:
        url = first_node_conf['api_url']

    def _login(url, priv_key, role_name, role_id=None):
        uid, uid_token = get_uid(url)
        l_result = login(url,
                         priv_key, uid, uid_token,
                         role_id=role_id,
                         sign_fmt=sign_fmt,
                         use_signtest=use_signtest, crypto_backend=crypto,
                         use_login_prefix=use_login_prefix,
                         pub_key_fmt=pub_key_fmt)
        return {
            'uid': uid,
            'uid_token': uid_token,
            'token': l_result['token'],
        }

    data = OrderedDict()
    for ind, params in conf.items():
        data[ind] = {}
        data[ind]['auth'] = {}
        data[ind]['auth']['common'] = _login(url, conf[ind]['priv_key'],
                                             'common', APLA_COMMON_ROLE_ID)
    first_node_data = tuple(data.items())[0][1]

    print("Installing roles ...")
    install_roles(url, first_node_conf['priv_key'],
                  first_node_data['auth']['common']['token'],
                  verify_cert=True)
    print("")

    print("Installing voting templates ...")
    install_voting_templates(url, first_node_conf['priv_key'],
                             first_node_data['auth']['common']['token'],
                             verify_cert=True)
    print("")

    print("Setting voting template id ...")
    edit_app_param(url, first_node_conf['priv_key'],
                   first_node_data['auth']['common']['token'],
                   'voting_sysparams_template_id', 2)
    print("")

    def _get_full_node_json(node_conf):
        return json.dumps({'tcp_address': node_conf['tcp_address'],
                           'api_address': node_conf['api_address'],
                           'key_id': node_conf['key_id'],
                           'public_key': node_conf['pub_key']})

    node1 = _get_full_node_json(first_node_conf)

    print("Updating 'first_node' parameter ...")
    edit_app_param(url, first_node_conf['priv_key'],
                   first_node_data['auth']['common']['token'],
                   'first_node', node1)
    print("")

    i = 1
    for ind in other_node_inds:
        print("Updating node owner name for node %s ..." % ind)
        w_result = edit_profile(url, conf[ind]['priv_key'],
                                data[ind]['auth']['common']['token'],
                                name="nodeowner%d" % i)
        print("")
        i += 1

    data[first_node_ind]['auth']['admin'] = _login(url,
                                               conf[first_node_ind]['priv_key'],
                                               'admin', APLA_ADMIN_ROLE_ID)

    # Assign Ala Consensus Role to accounts
    for ind in conf.keys():
        print("Assigning consensus role to node %s ..." % ind)
        assign_apla_consensus_role(url, first_node_conf['priv_key'],
                                   first_node_data['auth']['admin']['token'],
                                   conf[ind]['key_id'],
                                   verify_cert=True)
        print("")
        data[ind]['auth']['consensus'] = _login(url, conf[ind]['priv_key'],
                                                'consensus',
                                                APLA_CONSENSUS_ROLE_ID)

    i = 1
    for ind in other_node_inds:
        print("Creating voting #%d ..." % i)
        add_node_by_voting(url, conf[ind]['priv_key'],
                           data[ind]['auth']['consensus']['token'],
                           conf[ind]['tcp_address'],
                           conf[ind]['api_address'],
                           conf[ind]['pub_key'],
                           duration=1, key_id=conf[ind]['key_id'])
        print("")

        print("Updating voting #%d status ..." % i)
        update_voting_status(url, first_node_conf['priv_key'],
                             first_node_data['auth']['admin']['token'])
        print("")

        for _ind in conf.keys():
            print("Voting #%d: node %s owner votes ..." % (i, _ind))
            w_result = accept_voting_decision(url, conf[_ind]['priv_key'],
                                  data[_ind]['auth']['consensus']['token'], i)
            print("")
        i += 1

    print("Full Nodes Voting completed")


class NumOfNodesIsntSetError(Error): pass
class NumOfNodesIsntANumError(Error): pass

def get_voting_conf_and_url_from_env():
    num_of_nodes = os.environ.get('NUM_OF_NODES')
    if not num_of_nodes:
        raise NumOfNodesIsntSetError("The number of nodes isn't set")
    if not is_number(num_of_nodes):
        raise NumOfNodesIsntANumError("The number of nodes isn't a number")
    num_of_nodes = int(num_of_nodes)

    conf_main = get_vars_from_env(
        {
            'priv_key': ['GENESIS_NODE%d_OWNER_PRIV_KEY',
                         'APLA_NODE%d_OWNER_PRIV_KEY'],
            'key_id': ['GENESIS_NODE%d_OWNER_KEY_ID',
                       'APLA_NODE%d_OWNER_KEY_ID'],
            'pub_key': ['GENESIS_NODE%d_OWNER_PUB_KEY',
                        'APLA_NODE%d_OWNER_PUB_KEY'],
            'api_url': ['GENESIS_NODE%d_INT_API_URL',
                        'APLA_NODE%d_INT_API_URL'],
            'tcp_address': ['GENESIS_NODE%d_INT_TCP_ADDR',
                        'APLA_NODE%d_INT_TCP_ADDR'],
        }, num_of_nodes)

    conf_aux = get_vars_from_env(
        {
            'api_url': ['GENESIS_NODE%d_API_URL',
                        'APLA_NODE%d_API_URL'],
        }, num_of_nodes)

    return conf_main, tuple(conf_aux.items())[0][1]['api_url'],
    
if __name__ == '__main__':
    conf, url = get_voting_conf_and_url_from_env()
    update_full_nodes_by_voting(conf, url)
