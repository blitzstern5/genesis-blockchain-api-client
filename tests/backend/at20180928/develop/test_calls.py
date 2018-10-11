import os
import time
import logging
from nose import with_setup

from genesis_blockchain_tools.contract import Contract
from genesis_blockchain_tools.crypto.backend import (
    import_crypto_by_backend,
)

from genesis_blockchain_api_client.logging import setup_logging
from genesis_blockchain_api_client.backend.at20180928.develop.calls import (
    common_get_request, common_post_request, files_post_request, get_uid, login,
    get_contract_info, send_tx, get_tx_status, wait_tx_status
)
from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

from ....utils import is_number, is_string, save_keypair_as, save_signature_as

backend_version = get_latest_version()
#print("backend version: %s" % backend_version)
for option_name, option_value in version_to_options(backend_version).items():
    #print("backend option: %s='%s'" % (option_name, option_value))
    globals()[option_name] = option_value

use_mock = False
g_patcher, p_patcher = None, None
pub_key, uid = None, None
api_root_url = 'http://127.0.0.1:17301/api/v2'
logger = logging.getLogger(__name__)
crypto = import_crypto_by_backend('cryptography')
setup_logging()
basedir = os.path.abspath(os.path.dirname(__file__))

verify_cert = True

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def nontest_get_contract_info():
    uid, token = get_uid(api_root_url)
    priv_key, pub_key = crypto.gen_keypair()
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    result = get_contract_info(api_root_url, l_result['token'],
                               name='MainCondition') 
    assert 'id' in result and is_number(result['id'])
    assert 'state' in result and is_number(result['state'])
    assert 'active' in result
    assert 'fields' in result and type(result['fields']) == list

    result = get_contract_info(api_root_url, l_result['token'],
                               name='EditPage') 
    assert 'id' in result and is_number(result['id'])
    assert 'state' in result and is_number(result['state'])
    assert 'active' in result
    assert 'fields' in result and type(result['fields']) == list

@with_setup(my_setup, my_teardown)
def test_send_tx():
    uid, token = get_uid(api_root_url)
    priv_key = 'b2ec5aa72da2724e2bd55bdd5e443e090fdc53076c4080d7d36a4d98280669dc'
    pub_key = crypto.get_public_key(priv_key)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    result = get_contract_info(api_root_url, l_result['token'],
                               name='MainCondition') 
    assert 'id' in result and is_number(result['id'])
    assert 'state' in result and is_number(result['state'])
    assert 'active' in result
    assert 'fields' in result and type(result['fields']) == list

    c = Contract(schema=result, private_key=priv_key, params={})
    data = c.concat()
    s_result = send_tx(api_root_url, l_result['token'],
                       data={'contract1': data})
    assert type(s_result) == dict
    assert 'hashes' in s_result
    assert 'contract1' in s_result['hashes'] and len(s_result['hashes']['contract1']) > 32
    hashes = [n for n in s_result['hashes'].values()]

    #g_result = get_tx_status(api_root_url, hashes, l_result['token'])
    #assert 'results' in g_result and g_result['results']
    #for h in hashes:
    #    assert h in g_result['results']
    #    assert 'blockid' in g_result['results'][h]

    #time.sleep(3)
    #g_result = get_tx_status(api_root_url, hashes, l_result['token'])
    #for h in hashes:
    #    assert g_result['results'][h]['blockid']
    w_result = wait_tx_status(api_root_url, hashes, l_result['token'])
    print("w_result: %s" % w_result)

