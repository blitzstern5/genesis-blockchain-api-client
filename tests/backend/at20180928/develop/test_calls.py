import os
import time
import json
import re
import logging
import base64
import tempfile
from nose import with_setup

from genesis_blockchain_tools.contract import Contract
from genesis_blockchain_tools.crypto.genesis import public_key_to_address
from genesis_blockchain_tools.crypto.backend import (
    import_crypto_by_backend,
)

from genesis_blockchain_api_client.logging import setup_logging
from genesis_blockchain_api_client.backend.at20180928.develop.calls import (
    common_get_request, common_post_request, files_post_request, get_uid, login,
    get_contract_info, send_tx, get_tx_status, wait_tx_status,
    call_contract, call_multi_contract,
    get_list, get_obj_by_name, #update_obj_by_name,
    edit_app_param, edit_profile,
    detect_mime_type, detect_file_mime_type,
    upload_binary, upload_import_data_from_file,
    get_ecosystem_params, get_ecosystem_param, get_founder_account,
    fetch_buffer_data, fetch_imported_data, import_data, install_roles,
    install_voting_templates, assign_role, assign_apla_consensus_role,
    GENESIS_COMMON_ROLE_ID, APLA_COMMON_ROLE_ID,
    GENESIS_ADMIN_ROLE_ID, APLA_ADMIN_ROLE_ID,
    GENESIS_CONSENSUS_ROLE_ID, APLA_CONSENSUS_ROLE_ID,
    add_node_by_voting, update_voting_status,
    accept_voting_decision,
)
from genesis_blockchain_api_client.backend.at20180928.develop.errors import (
    TxStatusHasErrmsgError, TxStatusBlockIDIsEmptyError,
    TxStatusNoBlockIDKeyError,
    WaitTxStatusTimeoutError, WaitTxStatusMaxTriesExceededError,
)
from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

from ....utils import (
    is_number, is_string, save_keypair_as, save_signature_as, is_hash_string,
    Error, PrivKeyIsNotSetError
)

backend_version = get_latest_version()
for option_name, option_value in version_to_options(backend_version).items():
    globals()[option_name] = option_value

use_mock = False
g_patcher, p_patcher = None, None
pub_key, uid = None, None
api_root_url = 'http://127.0.0.1:17301/api/v2'
logger = logging.getLogger(__name__)
crypto = import_crypto_by_backend('cryptography')
setup_logging()
basedir = os.path.abspath(os.path.dirname(__file__))
FIXTURES_DIR = os.path.join(basedir, 'fixtures')
CONTRACTS_DIR = os.path.join(FIXTURES_DIR, 'contracts')
IMAGES_DIR = os.path.join(FIXTURES_DIR, 'images')

verify_cert = True

def my_setup():
    pass

def my_teardown():
    pass

def check_get_contract_info_result(result):
    assert 'id' in result and is_number(result['id'])
    assert 'state' in result and is_number(result['state'])
    assert 'active' in result
    assert 'fields' in result and type(result['fields']) == list

def get_priv_key_from_env(node_ind):
    assert is_number(node_ind)
    assert node_ind >= 1
    if node_ind == 1:
        priv_key = os.environ.get(
            'GENESIS_FOUNDER_PRIV_KEY',
                os.environ.get('APLA_FOUNDER_PRIV_KEY',
                    os.environ.get('GENESIS_NODE1_OWNER_PRIV_KEY',
                        os.environ.get('APLA_NODE1_OWNER_PRIV_KEY'))))
    else:
        priv_key = os.environ.get('GENESIS_NODE%d_OWNER_PRIV_KEY' % node_ind,
                   os.environ.get('APLA_NODE%d_OWNER_PRIV_KEY' % node_ind))
    if not priv_key:
        raise PrivKeyIsNotSetError(priv_key)
    return priv_key

@with_setup(my_setup, my_teardown)
def NOtest_get_priv_key_from_env():
    for node_ind in range(1, 6):
        try:
            priv_key = get_priv_key_from_env(node_ind)
            print("Node %d Private Key: %s" % (node_ind, priv_key))
        except PrivKeyIsNotSetError as e:
            print("Node %d Private Key isn't set" % node_ind)

@with_setup(my_setup, my_teardown)
def NOtest_get_contract_info():
    uid, token = get_uid(api_root_url)
    priv_key = get_priv_key_from_env(1)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    result = get_contract_info(api_root_url, l_result['token'],
                               name='MainCondition') 
    check_get_contract_info_result(result)
    result = get_contract_info(api_root_url, l_result['token'],
                               name='EditPage') 
    check_get_contract_info_result(result)

@with_setup(my_setup, my_teardown)
def NOtest_send_tx():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    result = get_contract_info(api_root_url, l_result['token'],
                               name='MainCondition') 
    check_get_contract_info_result(result)
    c = Contract(schema=result, private_key=priv_key, params={})
    data = c.concat()
    call_name = 'contract1'
    s_result = send_tx(api_root_url, l_result['token'],
                       data={call_name: data})
    check_send_tx_result(s_result)

def check_get_tx_status_result(token, tx_hashes, timeout_secs):
    end_time = time.time() + timeout_secs
    while True:
        e = None
        try:
            g_result = get_tx_status(api_root_url, tx_hashes, token)
        except (TxStatusHasErrmsgError, TxStatusBlockIDIsEmptyError,
                TxStatusNoBlockIDKeyError) as e:
            if time.time() > end_time:
                raise e
        except Exception as e:
            raise e
        else:
            break
        time.sleep(1)
    assert g_result
    assert type(g_result) == dict
    for h, h_res in g_result.items():
        assert is_hash_string(h)
        assert h_res
        assert type(h_res) == dict
        assert 'blockid' in h_res
        assert 'result' in h_res

@with_setup(my_setup, my_teardown)
def NOtest_get_tx_status():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    result = get_contract_info(api_root_url, l_result['token'],
                               name='MainCondition') 
    c = Contract(schema=result, private_key=priv_key, params={})
    data = c.concat()
    call_name = 'contract1'
    s_result = send_tx(api_root_url, l_result['token'],
                       data={call_name: data})
    check_send_tx_result(s_result, no_input_data=True)

    timeout_secs = 10

    tx_hashes = [n for n in s_result['hashes'].values()]
    check_get_tx_status_result(l_result['token'], tx_hashes, timeout_secs)

    tx_hashes = s_result['hashes']
    check_get_tx_status_result(l_result['token'], tx_hashes, timeout_secs)

    tx_hashes = s_result
    check_get_tx_status_result(l_result['token'], tx_hashes, timeout_secs)

def check_wait_tx_status_result(w_result):
    print("w_result: %s" % w_result)
    assert w_result
    assert type(w_result) == dict
    for h, data in w_result.items():
        assert is_hash_string(h)
        assert data
        assert type(data) == dict
        assert 'blockid' in data
        assert data['blockid']
        assert 'result' in data

@with_setup(my_setup, my_teardown)
def NOtest_wait_tx_status():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    result = get_contract_info(api_root_url, l_result['token'],
                               name='MainCondition') 
    c = Contract(schema=result, private_key=priv_key, params={})
    data = c.concat()
    call_name = 'contract1'
    s_result = send_tx(api_root_url, l_result['token'],
                       data={call_name: data})
    check_send_tx_result(s_result, no_input_data=True)

    timeout_secs = 10
    max_tries = 100
    gap_secs = 1

    w_result = wait_tx_status(api_root_url, s_result, l_result['token'],
                   timeout_secs=timeout_secs, max_tries=max_tries,
                   gap_secs=gap_secs, show_indicator=True, verify_cert=True)
    check_wait_tx_status_result(w_result)

@with_setup(my_setup, my_teardown)
def NOtest_call_contract():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    contract_name = 'MainCondition'
    params = {}
    
    s_result = call_contract(api_root_url, priv_key, l_result['token'],
                             contract_name, params, ecosystem_id=1,
                             verify_cert=True, wait_tx=False)
    check_send_tx_result(s_result)

    timeout_secs = 10
    max_tries = 100
    gap_secs = 1

    w_result = wait_tx_status(api_root_url, s_result, l_result['token'],
                   timeout_secs=timeout_secs, max_tries=max_tries,
                   gap_secs=gap_secs, show_indicator=True, verify_cert=True)
    check_wait_tx_status_result(w_result)

    w_result = call_contract(api_root_url, priv_key, l_result['token'],
                             contract_name, params, ecosystem_id=1,
                             verify_cert=True, wait_tx=True)
    check_wait_tx_status_result(w_result)

def check_send_tx_result(s_result, no_input_data=False):
    assert type(s_result) == dict
    assert 'hashes' in s_result
    assert s_result['hashes']
    assert type(s_result['hashes']) == dict
    assert len(s_result) >= 1

    if no_input_data:
        return

    assert 'input_data' in s_result
    assert s_result['input_data']
    assert type(s_result['input_data']) == dict

    assert len(s_result['input_data']) == len(s_result['hashes'])

    for call_name, h in s_result['hashes'].items():
        assert is_string(call_name) or is_number(call_name)
        assert is_hash_string(h)
        assert call_name in s_result['input_data']
        assert s_result['input_data'][call_name]
        assert type(s_result['input_data'][call_name]) == dict
                
@with_setup(my_setup, my_teardown)
def NOtest_call_multi_contract():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    data = [
        {'contract': 'MainCondition'},
        {'contract': 'MainCondition', 'params': {}},
        {'contract': 'MainCondition', 'params': None},
    ]
    s_result = call_multi_contract(api_root_url, priv_key, l_result['token'],
                                   data, ecosystem_id=1, verify_cert=True,
                                   wait_tx=False)
    check_send_tx_result(s_result)

    timeout_secs = 10
    max_tries = 100
    gap_secs = 1

    wait_tx_status(api_root_url, s_result, l_result['token'],
                   timeout_secs=timeout_secs, max_tries=max_tries,
                   gap_secs=gap_secs, show_indicator=True, verify_cert=True)

    w_result = call_multi_contract(api_root_url, priv_key, l_result['token'],
                                   data, ecosystem_id=1, verify_cert=True,
                                   wait_tx=True)
    check_wait_tx_status_result(w_result)

@with_setup(my_setup, my_teardown)
def NOtest_upload_import_data_from_file():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)

    path = os.path.join(CONTRACTS_DIR, 'empty.json')
    w_result = upload_import_data_from_file(api_root_url, priv_key,
                                            l_result['token'], path)
    check_wait_tx_status_result(w_result)

@with_setup(my_setup, my_teardown)
def NOtest_detect_mime_type():
    gif_content = b'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'
    mt = detect_mime_type(base64.b64decode(gif_content))
    assert mt == 'image/gif'

@with_setup(my_setup, my_teardown)
def NOtest_detect_file_mime_type():
    png_content = b'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAcCAYAAAB2+A+pAAABS2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxMzggNzkuMTU5ODI0LCAyMDE2LzA5LzE0LTAxOjA5OjAxICAgICAgICAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIi8+CiA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgo8P3hwYWNrZXQgZW5kPSJyIj8+IEmuOgAAA09JREFUSIm1lk1LMl0YgK9pdNQZR0FFsxSCMApJidCFRIsI2gW1bdU/eX9F1K7/YCDRJoKgDyQKQhCkRSFTlmN+jV85z6L3fVb14vQ83nAWw5xzXdznvs+cATCtjqmpKTMQCJiAGY/HTZ/PZ5mB1QXBYNDc3983FxYWTMDc29szj4+PLYsnsBibm5s8PDxQKBQAyGazRCIRUqmUJY5lcTgcxu/3k8lkCAQCKIrC0dERKysr4xXXajVEUUSWZba2thAEgXw+jyRJljg2q+JSqYSu67y+vtJqtahWq6yvr3N9fW2JIwL/WFnQaDSQJIlwOMzOzg7D4ZB8Pk+hUKDT6YzMsbzVmqbR6XRYW1vj9vaWVCrF3Nwcuq5b4lgWAwiCgN/v//08MzODKIrjFw8GA1RVRVVVRFHE5XJZZvxIbLfbeX9/p9vt0u12kSTJclf/SNxutxkMBhiGgaZpOBwO3G73+MWdTgdRFFEUhW63S7PZRJblL+cKgvD3xM1mk16vR6vVwjAMVFXF4XB8Odc0zb8n7vV6GIaB1+vF4XAQDAbxeDyWGD/e6kqlgsvlQtd1er0eqqqOX2yz2dA0jVarhdvt5uXlBbvdPn6xJEkMh0PK5TLlchlZlolGo5YYli8J+PyAeL1eJicnmZiYIBAIMBwOLTF+lLEsy8iyTKVSYXFxkWg0Sq1WG7/4+fkZWZbxeDw0Gg2Ab4/TdyHw74/XKLG7u0soFKJWq1GtVpFlGZfLRSwW4+zsDIBut8tgMODk5OR/WSPV2G63s729TSKR4OPjg7m5OXK5HIIgEAqFOD8/x+FwEIlEiMVi2Gw2+v0+p6enfyZOJBKsrq5yeHjI4+Mj8/PzxONxAoEAPp8Pt9tNq9Uim83idDpZWloinU5zdXVFu93+kjlSjVVVxeVyEQ6H0TSNfD6PoihcXFxwcHCAoiiEQiGKxSJ3d3fA50Vis32f10gZ39/fUy6XcTqdJJNJ+v0+kiSRTqdpt9s4nU6KxSKZTAbDMBBFkaenJ+r1+rfMkZtrY2ODRCIBfDaQYRjouo6u6ySTSer1OjabjVAoRKlUIpfL8fb29udigNnZWaanpzFNk8vLS3q93u93y8vLqKpKv9/n5ubm29r+F78AmGZ4Lz2bZYkAAAAASUVORK5CYII='
    tmp_png_file = tempfile.mktemp()
    tmp_png_path = str(tmp_png_file)
    with open(tmp_png_path, 'bw') as f:
        f.write(base64.b64decode(png_content))
        f.close()
    mt = detect_file_mime_type(tmp_png_path)
    assert mt == 'image/png'

@with_setup(my_setup, my_teardown)
def NOtest_upload_binary():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)

    name = 'my_string'
    data = 'some string'.encode()
    app_id = 1
    mime_type='text/plain'
    w_result = upload_binary(api_root_url, priv_key, l_result['token'], name,
                             data, app_id=app_id, mime_type=mime_type)
    check_wait_tx_status_result(w_result)

    assert len(w_result) == 1
    result = [w_result[result] for result in w_result][0]['result']
    assert is_number(result)

@with_setup(my_setup, my_teardown)
def NOtest_get_list():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)

    kind = 'app_params'
    result = get_list(api_root_url, priv_key, l_result['token'], kind)
    assert result
    assert type(result) == dict
    assert 'count' in result
    assert is_number(result['count'])
    assert 'list' in result
    assert type(result['list']) == list

@with_setup(my_setup, my_teardown)
def NOtest_get_obj_by_name():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)

    kind = 'app_params'
    name = 'voting_sysparams_template_id'
    result = get_obj_by_name(api_root_url, priv_key, l_result['token'], kind,
                            name)
    assert result
    assert type(result) == dict
    assert 'name' in result
    assert 'value' in result
    assert 'app_id' in result
    assert 'conditions' in result
    assert 'ecosystem' in result

@with_setup(my_setup, my_teardown)
def NOtest_edit_app_param():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)

    name = 'voting_sysparams_template_id'
    value = 2
    w_result = edit_app_param(api_root_url, priv_key, l_result['token'],
                              name, value)
    check_wait_tx_status_result(w_result)

@with_setup(my_setup, my_teardown)
def NOtest_edit_profile():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)

    name = 'New Name'
    information = 'Some about'
    image_id = 1

    w_result = edit_profile(api_root_url, priv_key, l_result['token'],
                            name=name, information=information,
                            image_id=image_id)
    check_wait_tx_status_result(w_result)

@with_setup(my_setup, my_teardown)
def NOtest_get_ecosystem_params():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    result = get_ecosystem_params(api_root_url, priv_key, l_result['token'],
                                  ecosystem_id=1, names=[])
    assert result
    assert type(result) in [tuple, list]
    for item in result:
        assert item
        assert type(item) == dict
        assert 'id' in item
        assert is_number(item['id'])
        assert 'name' in item
        assert is_string(item['name'])
        assert 'value' in item
        assert is_string(item['value'])

@with_setup(my_setup, my_teardown)
def NOtest_get_ecosystem_param():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    name = 'max_tx_block_per_user'
    value, id = get_ecosystem_param(api_root_url, priv_key, l_result['token'],
                                 name, ecosystem_id=1)
    assert value
    assert is_string(value)
    assert id
    assert is_number(id)

@with_setup(my_setup, my_teardown)
def NOtest_get_founder_account():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    value = get_founder_account(api_root_url, priv_key, l_result['token'],
                                ecosystem_id=1)
    assert value
    assert is_number(value)

@with_setup(my_setup, my_teardown)
def NOtest_fetch_buffer_data():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    result = fetch_buffer_data(api_root_url, priv_key, l_result['token'])
    assert result
    assert type(result) == dict
    assert 'count' in result
    assert is_number(result['count'])
    assert 'list' in result
    assert type(result['list']) == list

@with_setup(my_setup, my_teardown)
def NOtest_fetch_imported_data():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    result = fetch_imported_data(api_root_url, priv_key, l_result['token'])
    assert result
    assert type(result) == list
    for item in result:
        assert item
        assert type(item) == dict
        assert 'Data' in item
        assert item['Data']

@with_setup(my_setup, my_teardown)
def NOtest_import_data():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    data = fetch_imported_data(api_root_url, priv_key, l_result['token'])
    w_result = import_data(api_root_url, priv_key, l_result['token'], data,
                           verify_cert=True)
    check_wait_tx_status_result(w_result)

@with_setup(my_setup, my_teardown)
def NOtest_install_roles():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    w_result = install_roles(api_root_url, priv_key, l_result['token'],
                             verify_cert=True)
    check_wait_tx_status_result(w_result)

@with_setup(my_setup, my_teardown)
def NOtest_install_voting_templates():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    w_result = install_voting_templates(api_root_url, priv_key,
                                        l_result['token'], verify_cert=True)
    check_wait_tx_status_result(w_result)

@with_setup(my_setup, my_teardown)
def NOtest_assign_role():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)
    pub_key = bytes.fromhex(crypto.get_public_key(priv_key))
    account = public_key_to_address(pub_key)
    role_id = APLA_CONSENSUS_ROLE_ID

    w_result = assign_role(api_root_url, priv_key, l_result['token'],
                           account, role_id, verify_cert=True)
    check_wait_tx_status_result(w_result)

@with_setup(my_setup, my_teardown)
def NOtest_assign_apla_consensus_role():
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)
    pub_key = bytes.fromhex(crypto.get_public_key(priv_key))
    account = public_key_to_address(pub_key)
    w_result = assign_apla_consensus_role(api_root_url, priv_key,
                                          l_result['token'], account,
                                          verify_cert=True)
    check_wait_tx_status_result(w_result)

@with_setup(my_setup, my_teardown)
def test_add_node_by_voting():
    # Auth 1
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)
    pub_key = crypto.get_public_key(priv_key)
    account = public_key_to_address(bytes.fromhex(pub_key))

    tcp_address = '127.0.0.1:7078'
    api_address = 'http://localhost:7001' #/api/v2'

    # Auth 2
    priv_key2 = get_priv_key_from_env(2)
    uid2, token2 = get_uid(api_root_url)
    l_result2 = login(api_root_url, priv_key2, uid2, token2, sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)
    pub_key2 = crypto.get_public_key(priv_key2)
    account2 = public_key_to_address(bytes.fromhex(pub_key2))
    tcp_address2 = '127.0.0.1:7012'
    api_address2 = 'http://localhost:7002' #/api/v2'


    # Auth 3
    priv_key3 = get_priv_key_from_env(3)
    uid3, token3 = get_uid(api_root_url)
    l_result3 = login(api_root_url, priv_key3, uid3, token3, sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)
    pub_key3 = crypto.get_public_key(priv_key3)
    account3 = public_key_to_address(bytes.fromhex(pub_key3))
    tcp_address3 = '127.0.0.1:7013'
    api_address3 = 'http://localhost:7003' #/api/v2'


    # RolesInstall
    w_result = install_roles(api_root_url, priv_key, l_result['token'],
                             verify_cert=True)
    check_wait_tx_status_result(w_result)

    # VotingTemplateInstall
    w_result = install_voting_templates(api_root_url, priv_key,
                                        l_result['token'], verify_cert=True)
    check_wait_tx_status_result(w_result)

    # Edit Voting Sysparams Template ID
    w_result = edit_app_param(api_root_url, priv_key, l_result['token'],
                              'voting_sysparams_template_id', 2)
    check_wait_tx_status_result(w_result)

    # Edit  first node app param
    node1 = json.dumps({'tcp_address': tcp_address,
                        'api_address': api_address,
                        'key_id': str(account),
                        'public_key': pub_key})
    print("node1: %s" % node1)
    w_result = edit_app_param(api_root_url, priv_key, l_result['token'],
                              'first_node', node1)
    check_wait_tx_status_result(w_result)


    # Update Node 2 owner name
    try:
        w_result = edit_profile(api_root_url, priv_key2, l_result2['token'],
                                name="nodeowner1")
        check_wait_tx_status_result(w_result)
    except Exception as e:
        print("e: %s" % e)

    # Update Node 3 owner name
    try:
        w_result = edit_profile(api_root_url, priv_key3, l_result3['token'],
                                name="nodeowner2")
        check_wait_tx_status_result(w_result)
    except Exception as e:
        print("e: %s" % e)

    # Loging with ADMIN role
    uid_a, token_a = get_uid(api_root_url)
    l_result_a = login(api_root_url, priv_key, uid_a, token_a,
                       sign_fmt=sign_fmt, role_id=APLA_ADMIN_ROLE_ID,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)

    # Assign Ala Consensus Role to accounts
    w_result = assign_apla_consensus_role(api_root_url, priv_key,
                                          l_result_a['token'], account2,
                                          verify_cert=True)
    check_wait_tx_status_result(w_result)

    w_result = assign_apla_consensus_role(api_root_url, priv_key,
                                          l_result_a['token'], account3,
                                          verify_cert=True)
    check_wait_tx_status_result(w_result)
    w_result = assign_apla_consensus_role(api_root_url, priv_key,
                                          l_result_a['token'], account,
                                          verify_cert=True)
    check_wait_tx_status_result(w_result)

    # Login with CONSENSUS role
    uid_c, token_c = get_uid(api_root_url)
    l_result_c = login(api_root_url, priv_key, uid_c, token_c,
                       sign_fmt=sign_fmt, role_id=APLA_CONSENSUS_ROLE_ID,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)

    uid_c2, token_c2 = get_uid(api_root_url)
    l_result_c2 = login(api_root_url, priv_key2, uid_c2, token_c2,
                        sign_fmt=sign_fmt, role_id=APLA_CONSENSUS_ROLE_ID,
                        use_signtest=use_signtest, crypto_backend=crypto,
                        use_login_prefix=use_login_prefix,
                        pub_key_fmt=pub_key_fmt)

    uid_c3, token_c3 = get_uid(api_root_url)
    l_result_c3 = login(api_root_url, priv_key3, uid_c3, token_c3,
                        sign_fmt=sign_fmt, role_id=APLA_CONSENSUS_ROLE_ID,
                        use_signtest=use_signtest, crypto_backend=crypto,
                        use_login_prefix=use_login_prefix,
                        pub_key_fmt=pub_key_fmt)

    ### Voting 1 

    # Add Node By Voting, votes Node 2 Owner
    try:
        w_result = add_node_by_voting(api_root_url, priv_key2,
                                      l_result_c2['token'],
                                      tcp_address2, api_address2, pub_key2,
                                      duration=1)
        check_wait_tx_status_result(w_result)
    except TxStatusHasErrmsgError as e:
        print("ERROR: %s" % e)

    # Update Voting Status
    try:
        update_voting_status(api_root_url, priv_key, l_result_a['token'])
    except Exception as e:
        print("e2: %s" % e)

    # Accept Voting Decission
    try:
        w_result = accept_voting_decision(api_root_url, priv_key,
                                      l_result_c['token'], 1)
        check_wait_tx_status_result(w_result)
    #except TxStatusHasErrmsgError as e:
    except Exception as e:
        print("e: %s" % e)
    try:
        w_result = accept_voting_decision(api_root_url, priv_key2,
                                          l_result_c2['token'], 1)
        check_wait_tx_status_result(w_result)
    #except TxStatusHasErrmsgError as e:
    except Exception as e:
        print("e2: %s" % e)
    try:
        w_result = accept_voting_decision(api_root_url, priv_key3,
                                          l_result_c3['token'], 1)
        check_wait_tx_status_result(w_result)
    #except TxStatusHasErrmsgError as e:
    except Exception as e:
        print("e3: %s" % e)

    #### Voting 2 

    # Add Node By Voting, votes Node 3 Owner
    try:
        w_result = add_node_by_voting(api_root_url, priv_key3,
                                      l_result_c3['token'],
                                      tcp_address3, api_address3, pub_key3,
                                      duration=1, timeout_secs=201,
                                      max_tries=201)
        check_wait_tx_status_result(w_result)
    except TxStatusHasErrmsgError as e:
        print("ERROR: %s" % e)

    # Update Voting Status
    try:
        update_voting_status(api_root_url, priv_key, l_result_a['token'],
                             timeout_secs=202, max_tries=202)
    except Exception as e:
        print("e2: %s" % e)

    ## Accept Voting Decission
    try:
        w_result = accept_voting_decision(api_root_url, priv_key3,
                                          l_result_c3['token'], 2,
                                          timeout_secs=203, max_tries=203)
        check_wait_tx_status_result(w_result)
    except Exception as e:
        print("e: %s" % e)
    try:
        w_result = accept_voting_decision(api_root_url, priv_key2,
                                          l_result_c2['token'], 2,
                                          timeout_secs=204, max_tries=204)
        check_wait_tx_status_result(w_result)
    except Exception as e:
        print("e2: %s" % e)
    try:
        w_result = accept_voting_decision(api_root_url, priv_key,
                                          l_result_c['token'], 2,
                                          timeout_secs=205, max_tries=205)
        check_wait_tx_status_result(w_result)
    except Exception as e:
        print("e3: %s" % e)

@with_setup(my_setup, my_teardown)
def NOtest_accept_voting_desicion():
    # Auth 1
    priv_key = get_priv_key_from_env(1)
    uid, token = get_uid(api_root_url)
    l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)
    pub_key = crypto.get_public_key(priv_key)
    account = public_key_to_address(bytes.fromhex(pub_key))

    tcp_address = '127.0.0.1:7078'
    api_address = 'http://localhost:7001' #/api/v2'

    # Auth 2
    priv_key2 = get_priv_key_from_env(2)
    uid2, token2 = get_uid(api_root_url)
    l_result2 = login(api_root_url, priv_key2, uid2, token2, sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)
    pub_key2 = crypto.get_public_key(priv_key2)
    account2 = public_key_to_address(bytes.fromhex(pub_key2))
    tcp_address2 = '127.0.0.1:7012'
    api_address2 = 'http://localhost:7002' #/api/v2'

    # Auth 3
    priv_key3 = get_priv_key_from_env(3)
    uid3, token3 = get_uid(api_root_url)
    l_result3 = login(api_root_url, priv_key3, uid3, token3, sign_fmt=sign_fmt,
                     use_signtest=use_signtest, crypto_backend=crypto,
                     use_login_prefix=use_login_prefix,
                     pub_key_fmt=pub_key_fmt)
    pub_key3 = crypto.get_public_key(priv_key3)
    account3 = public_key_to_address(bytes.fromhex(pub_key3))
    tcp_address3 = '127.0.0.1:7013'
    api_address3 = 'http://localhost:7003' #/api/v2'

    # Login with ADMIN role
    uid_a, token_a = get_uid(api_root_url)
    l_result_a = login(api_root_url, priv_key, uid_a, token_a,
                       sign_fmt=sign_fmt, role_id=APLA_ADMIN_ROLE_ID,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)

    # Login with CONSENSUS role
    uid_c, token_c = get_uid(api_root_url)
    l_result_c = login(api_root_url, priv_key, uid_c, token_c,
                       sign_fmt=sign_fmt, role_id=APLA_CONSENSUS_ROLE_ID,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)

    uid_c2, token_c2 = get_uid(api_root_url)
    l_result_c2 = login(api_root_url, priv_key2, uid_c2, token_c2,
                        sign_fmt=sign_fmt, role_id=APLA_CONSENSUS_ROLE_ID,
                        use_signtest=use_signtest, crypto_backend=crypto,
                        use_login_prefix=use_login_prefix,
                        pub_key_fmt=pub_key_fmt)

    uid_c3, token_c3 = get_uid(api_root_url)
    l_result_c3 = login(api_root_url, priv_key3, uid_c3, token_c3,
                        sign_fmt=sign_fmt, role_id=APLA_CONSENSUS_ROLE_ID,
                        use_signtest=use_signtest, crypto_backend=crypto,
                        use_login_prefix=use_login_prefix,
                        pub_key_fmt=pub_key_fmt)

    ### Voting 2 

    # Add Node By Voting, votes Node 3 Owner
    try:
        w_result = add_node_by_voting(api_root_url, priv_key3,
                                      l_result_c3['token'],
                                      tcp_address3, api_address3, pub_key3,
                                      duration=1, timeout_secs=200,
                                      max_tries=200)
        check_wait_tx_status_result(w_result)
    except TxStatusHasErrmsgError as e:
        print("ERROR: %s" % e)

    # Update Voting Status
    try:
        update_voting_status(api_root_url, priv_key, l_result_a['token'],
                             timeout_secs=200, max_tries=200)
    except Exception as e:
        print("e2: %s" % e)

    ## Accept Voting Decission
    try:
        w_result = accept_voting_decision(api_root_url, priv_key3,
                                          l_result_c3['token'], 2,
                                          timeout_secs=200, max_tries=200)
        check_wait_tx_status_result(w_result)
    except Exception as e:
        print("e: %s" % e)
    try:
        w_result = accept_voting_decision(api_root_url, priv_key,
                                          l_result_c['token'], 2,
                                          timeout_secs=200, max_tries=200)
        check_wait_tx_status_result(w_result)
    except Exception as e:
        print("e3: %s" % e)
    try:
        w_result = accept_voting_decision(api_root_url, priv_key2,
                                          l_result_c2['token'], 2,
                                          timeout_secs=200, max_tries=200)
        check_wait_tx_status_result(w_result)
    except Exception as e:
        print("e2: %s" % e)
