from time import time, sleep
import json
import logging 
import urllib

import puremagic
from puremagic.main import PureError

from genesis_blockchain_tools.contract import Contract
from genesis_blockchain_tools.utils import find_mime_type_recursive
from genesis_blockchain_tools.crypto.genesis import public_key_to_key_id

from ....utils import is_string, is_hash_string
from ....calls import (
    GENESIS_COMMON_ROLE_ID, APLA_COMMON_ROLE_ID,
    GENESIS_ADMIN_ROLE_ID,  APLA_ADMIN_ROLE_ID,
    GENESIS_CONSENSUS_ROLE_ID, APLA_CONSENSUS_ROLE_ID,
    common_get_request, common_post_request, files_post_request, get_uid, login,
    errmsg_to_string, 
)
from .errors import (Error, ExceptionWithKwargs,
    TxStatusHasErrmsgError, TxStatusBlockIDIsEmptyError,
    TxStatusNoBlockIDKeyError, WaitTxStatusTimeoutError,
    WaitTxStatusMaxTriesExceededError,
)

logger = logging.getLogger(__name__)

def get_contract_info(url, token, name, verify_cert=True):
    return common_get_request(
        url + '/contract/' + name,
        headers={'Authorization': 'Bearer ' + token},
        verify_cert=verify_cert
    )

def send_tx(url, token, data='', verify_cert=True, send_pub_key=True):
    return files_post_request(
        url + '/sendTx',
        headers={'Authorization': 'Bearer ' + token},
        data=data,
        verify_cert=verify_cert
    )

class TxHashesFormatError(Error): pass

def get_tx_status(url, tx_hashes, token, verify_cert=True):
    if is_hash_string(tx_hashes):
        _tx_hashes = [tx_hashes]
    elif type(tx_hashes) in [list, tuple]:
        _tx_hashes = tx_hashes
    elif type(tx_hashes) in [dict]:
        if 'hashes' in tx_hashes:
            _tx_hashes = [h for h in tx_hashes['hashes'].values()]
        else:
            _tx_hashes = [n for n in tx_hashes.values()]
    else:
        raiseTxHashesFormatError(tx_hashes)

    logger.debug("    requesting /txstatus/%s ..." % _tx_hashes)
    g_result = common_post_request(
        url + '/txstatus',
        headers={'Authorization': 'Bearer ' + token},
        params={'data': json.dumps({'hashes': _tx_hashes})},
        verify_cert=verify_cert
    )
    results = {}
    for h in _tx_hashes:
        result = g_result['results'][h]
        logger.debug("result: %s" % result)
        if 'errmsg' in result:
            logger.debug("    'errmsg' key is present")
            raise TxStatusHasErrmsgError(errmsg_to_string(result['errmsg']),
                        url=url, tx_hash=h, token=token,
                        verify_cert=verify_cert, result=result)

        if 'blockid' in result:
            logger.debug("    'blockid' key is present")
            if not result['blockid']:
                logger.debug("'blockid' is empty")
                raise TxStatusBlockIDIsEmptyError("blockid is EMPTY", url=url,
                        tx_hash=h, token=token, verify_cert=verify_cert,
                        result=result)
        else:
            logger.debug("    'blockid' key is absent")
            raise TxStatusNoBlockIDKeyError("'blockid key is absent", url=url,
                    tx_hash=h, token=token, verify_cert=verify_cert,
                    result=result)
        results[h] = result
    return results

def wait_tx_status(url, tx_hashes, token, timeout_secs=100, max_tries=100,
                   gap_secs=1, show_indicator=True, verify_cert=True,
                   indicator_type='timeout-cnt-max_tries',
                   indicator_str="Waiting (%d seconds) for the completion of the transaction (try %d/%d) ..."):

    logger.debug("gap_secs: %d timeout_secs: %d max_tries: %d" %(gap_secs,
        timeout_secs, max_tries))
    end_time = time() + timeout_secs
    results = None
    cnt = 1
    while True:
        if show_indicator:
            if indicator_type == 'timeout-cnt-max_tries':
                print(indicator_str % (timeout_secs, cnt, max_tries))
        logger.debug("timeout: %d try %d/%d" % (timeout_secs, cnt, max_tries))
        try:
            results = get_tx_status(url, tx_hashes, token,
                                    verify_cert=verify_cert)
            return results
        except (TxStatusHasErrmsgError) as e:
            logger.debug("errmsg: %s" % e)
            raise e
        except (TxStatusBlockIDIsEmptyError, TxStatusNoBlockIDKeyError) as e:
            logger.debug("e: %s" % e)
            if time() > end_time:
                msg = "time '%d' exceeded" % timeout_secs
                logger.debug(msg)
                raise WaitTxStatusTimeoutError(msg, url=url, tx_hash=tx_hashes,
                        token=token, verify_cert=verify_cert, result=results,
                        timeout_secs=timeout_secs, max_tries=max_tries,
                        gap_secs=gap_secs, tx_status_error=e)
            if cnt > max_tries:
                msg = "cnt: '%d', max tries '%d' exceeded" % (cnt, max_tries)
                logger.debug(msg)
                raise WaitTxStatusMaxTriesExceededError(msg, url=url,
                        tx_hash=tx_hashes, token=token, verify_cert=verify_cert,
                        result=results, timeout_secs=timeout_secs,
                        max_tries=max_tries, gap_secs=gap_secs,
                        tx_status_error=e)
        cnt += 1
        sleep(gap_secs)

def call_contract(url, priv_key, token, name, params, ecosystem_id=1,
                  call_name='call_0', verify_cert=True, wait_tx=True,
                  timeout_secs=20, max_tries=20, gap_secs=1):
    schema = get_contract_info(url, token, name, verify_cert=verify_cert)
    contract = Contract(schema=schema, private_key=priv_key,
                        ecosystem_id=ecosystem_id, params=params)
    bin_data = contract.concat()
    if not call_name:
        call_name = name
    s_result = send_tx(url, token, {call_name: bin_data},
                       verify_cert=verify_cert)
    s_result['input_data'] = {call_name: {'contract': name, 'params': params}}

    if wait_tx:
        return wait_tx_status(url, s_result, token,
                       timeout_secs=timeout_secs, max_tries=max_tries,
                       gap_secs=gap_secs, show_indicator=True, verify_cert=True)
    else:
        return s_result

def call_multi_contract(url, priv_key, token, data, ecosystem_id=1,
                        call_prefix='call_', verify_cert=True, wait_tx=True,
                        timeout_secs=20, max_tries=20, gap_secs=1):
    all_bin_data = {}
    input_data = {}
    schemas = {}
    i = 0
    for item in data:
        if 'contract' not in item:
            logger.warning("data item has no 'contract' key")
            continue
        if item['contract'] not in schemas:
            schemas[item['contract']] = {}
        if 'schema' not in schemas[item['contract']]:
            schemas[item['contract']]['schema'] = get_contract_info(url, token,
                                      item['contract'], verify_cert=verify_cert)
        if 'cnt' not in schemas[item['contract']]:
            schemas[item['contract']]['cnt'] = 0
        schemas[item['contract']]['cnt'] += 1
        if 'ecosystem_id' in item:
            _ecosystem_id = item['ecosystem_id']
        else:
            _ecosystem_id = ecosystem_id
        if 'params' in item and item['params']:
            params = item['params']
        else:
            params = {}
        call_name = "%s%d" % (call_prefix, i)
        contract = Contract(schema=schemas[item['contract']]['schema'],
                            private_key=priv_key, ecosystem_id=_ecosystem_id,
                            params=params)
        bin_data = contract.concat()
        all_bin_data[call_name] = bin_data
        input_data[call_name] = item
        i += 1
    s_result = send_tx(url, token, data=all_bin_data, verify_cert=verify_cert)
    s_result['input_data'] = input_data

    if wait_tx:
        return wait_tx_status(url, s_result, token,
                       timeout_secs=timeout_secs, max_tries=max_tries,
                       gap_secs=gap_secs, show_indicator=True, verify_cert=True)
    else:
        return s_result

def detect_mime_type(data):
    try:
        m = find_mime_type_recursive(puremagic.magic_string(data))
    except PureError as e:
        m = None
    if m:
        return m

def detect_file_mime_type(path):
    try:
        m = find_mime_type_recursive(puremagic.magic_file(path))
    except PureError:
        m = None
    if m:
        return m

def upload_binary(url, priv_key, token, name, data, app_id=1,
                  mime_type='application/octet-stream', ecosystem_id=1,
                  auto_detect_mime_type=True, verify_cert=True,
                  wait_tx=True, timeout_secs=20, max_tries=20, gap_secs=1):
    if auto_detect_mime_type:
        mime_type = detect_mime_type(data)
    params = {'Name': name, 'Data': data, 'ApplicationId': int(app_id),
              'MimeType': mime_type}
    return call_contract(url, priv_key, token, 'UploadBinary', params,
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

def upload_import_data_from_file(url, priv_key, token, path, ecosystem_id=1,
                            verify_cert=True, wait_tx=True, timeout_secs=20,
                            max_tries=20, gap_secs=1):
    params = {'Data': path}
    return call_contract(url, priv_key, token, 'ImportUpload', params,
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

def get_list(url, priv_key, token, kind, ecosystem_id=1, verify_cert=True):
    return common_get_request(
        "%s/list%s" % (url, "/" + kind if kind else ""),
        headers={'Authorization': 'Bearer ' + token}, verify_cert=verify_cert
    )

class ObjNotFoundError(Error): pass

def get_obj_by_name(url, priv_key, token, kind, name, ecosystem_id=1,
                    verify_cert=True):
    l = get_list(url, priv_key, token, kind, ecosystem_id=ecosystem_id,
                 verify_cert=verify_cert)
    if int(l['count']) > 0:
        for item in l['list']:
            if name == item['name']:
                return item
    return ObjNotFoundError("object with name '%s' not found" % name)

def edit_app_param(url, priv_key, token, name, value, ecosystem_id=1,
                   verify_cert=True, wait_tx=True, timeout_secs=20,
                   max_tries=20, gap_secs=1):
    obj = get_obj_by_name(url, priv_key, token, 'app_params', name,
                          ecosystem_id=ecosystem_id, verify_cert=verify_cert)
    params = {'Id': obj['id'], 'Value': value, 'Conditions': obj['conditions']}
    return call_contract(url, priv_key, token, 'EditAppParam', params,
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

def edit_profile(url, priv_key, token, ecosystem_id=1, verify_cert=True,
                 wait_tx=True, timeout_secs=20, max_tries=20, gap_secs=1,
                 **kwargs):
    params = {}
    if 'name' in kwargs:
        params['member_name'] = kwargs.get('name')
    if 'information' in kwargs:
        params['information'] = kwargs.get('information')
    if 'image_id' in kwargs:
        params['image_id'] = kwargs.get('image_id')
    return call_contract(url, priv_key, token, 'ProfileEdit', params,
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

def get_ecosystem_params(url, priv_key, token, ecosystem_id=1, names=[],
                         verify_cert=True):
    params = {}
    result = common_get_request(
        url + "/ecosystemparams", params,
        headers={'Authorization': 'Bearer ' + token}, verify_cert=verify_cert
    )
    return result['list']

def get_ecosystem_param(url, priv_key, token, name, ecosystem_id=1,
                        verify_cert=True):
    result = common_get_request(
        url + "/ecosystemparam/" + name,
        headers={'Authorization': 'Bearer ' + token}, verify_cert=verify_cert
    )
    return result['value'], result['id']

def get_founder_account(url, priv_key, token, ecosystem_id=1, verify_cert=True):
    value, _= get_ecosystem_param(url, priv_key, token, 'founder_account',
                               ecosystem_id=ecosystem_id,
                               verify_cert=verify_cert)
    return int(value)

def fetch_buffer_data(url, priv_key, token, verify_cert=True):
    return common_get_request(
        url + "/list/buffer_data",
        headers={'Authorization': 'Bearer ' + token}, verify_cert=verify_cert
    )

class FetchImportDataError(Error): pass

def fetch_imported_data(url, priv_key, token, verify_cert=True):
    founder_account = get_founder_account(url, priv_key, token, ecosystem_id=1,
                                          verify_cert=verify_cert)
    data = fetch_buffer_data(url, priv_key, token, verify_cert=verify_cert)
    for item in data['list']:
        if item['key'] == 'import' \
        and int(item['member_id']) == founder_account:
            return json.loads(item['value'])['data']
    raise FetchImportDataError("'import' key not found or 'member_id': %s != 'founder_account': %s" % (item['member_id'], founder_account))

def import_data(url, priv_key, token, data, ecosystem_id=1, verify_cert=True,
                wait_tx=True, timeout_secs=20, max_tries=20, gap_secs=1):
    data = [{'contract': 'Import', 'params': params} for params in data]
    return call_multi_contract(url, priv_key, token, data,
                               ecosystem_id=ecosystem_id, call_prefix='call_',
                               verify_cert=verify_cert, wait_tx=wait_tx,
                               timeout_secs=timeout_secs, max_tries=max_tries,
                               gap_secs=gap_secs)


### Full Nodes Voting ### begin ###

def url_to_address(url):
    return urllib.parse.urlunparse(tuple(urllib.parse.urlparse(url))[:-4] + tuple((',' * 3).split(',')))

def install_roles(url, priv_key, token, ecosystem_id=1, verify_cert=True,
                  wait_tx=True, timeout_secs=20, max_tries=20, gap_secs=1):
    s_result = call_contract(url, priv_key, token, 'RolesInstall', {},
                             ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                             wait_tx=wait_tx, timeout_secs=timeout_secs,
                             max_tries=max_tries, gap_secs=gap_secs)
    return s_result

def install_voting_templates(url, priv_key, token, ecosystem_id=1,
                             verify_cert=True, wait_tx=True, timeout_secs=20,
                             max_tries=20, gap_secs=1):
    return call_contract(url, priv_key, token, 'VotingTemplatesInstall', {},
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

def assign_role(url, priv_key, token, account, role_id, ecosystem_id=1,
                verify_cert=True, wait_tx=True, timeout_secs=20, max_tries=20,                  gap_secs=1):
    params = {'member_id': account, "rid": role_id}
    return call_contract(url, priv_key, token, 'RolesAssign', params,
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

def assign_apla_consensus_role(url, priv_key, token, account, ecosystem_id=1,
                               verify_cert=True, wait_tx=True, timeout_secs=20,
                               max_tries=20, gap_secs=1):
    return assign_role(url, priv_key, token, account, APLA_CONSENSUS_ROLE_ID,
                       ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                       wait_tx=wait_tx, timeout_secs=timeout_secs,
                       max_tries=max_tries, gap_secs=gap_secs)

def add_node_by_voting(url, priv_key, token, tcp_address, api_address, pub_key,
                       key_id=None, duration=1, ecosystem_id=1,
                       verify_cert=True, wait_tx=True, timeout_secs=20,
                       max_tries=20, gap_secs=1):
    if not key_id:
        key_id = public_key_to_key_id(bytes.fromhex(pub_key))
    params = {'TcpAddress': tcp_address, 'ApiAddress': api_address,
              'KeyId': key_id, 'PubKey': pub_key, 'Duration': duration}
    return call_contract(url, priv_key, token, 'VotingNodeAdd', params,
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

def update_voting_status(url, priv_key, token, ecosystem_id=1,
                         verify_cert=True, wait_tx=True, timeout_secs=20,
                         max_tries=20, gap_secs=1):
    return call_contract(url, priv_key, token, 'VotingStatusUpdate', {},
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

def accept_voting_decision(url, priv_key, token, account, ecosystem_id=1,
                           verify_cert=True, wait_tx=True, timeout_secs=20,
                           max_tries=20, gap_secs=1):
    params = {"votingID": account, "RoleId": APLA_CONSENSUS_ROLE_ID}
    return call_contract(url, priv_key, token, 'VotingDecisionAccept', params,
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

### Full Nodes Voting #### end ####


### UpdateSysParam ### begin ###

def update_sys_param(url, priv_key, token, name, value, ecosystem_id=1,
                     verify_cert=True, wait_tx=True, timeout_secs=20,
                     max_tries=20, gap_secs=1):
    params = {"Name": str(name).rstrip(), "Value": str(value).rstrip()}
    return call_contract(url, priv_key, token, 'UpdateSysParam', params,
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

def update_sys_params(url, priv_key, token, name_value_dict, ecosystem_id=1,
                     verify_cert=True, wait_tx=True, timeout_secs=20,
                     max_tries=20, gap_secs=1):
    data = []
    for name, value in name_value_dict.items():
        data.append({
            'contract': 'UpdateSysParam',
            'params': {"Name": str(name).rstrip(), "Value": str(value).rstrip()}
        })

    return call_multi_contract(url, priv_key, token, data,
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)


### UpdateSysParam #### end ####


### Update Keys ### begin ###

def update_keys_raw(url, priv_key, token, keys_data, ecosystem_id=1,
                    verify_cert=True, wait_tx=True, timeout_secs=20,
                    max_tries=20, gap_secs=1):
    data = []
    for key_id, key_data in keys_data.items():
        data.append({
            'contract': 'UpdateKeysRaw',
            'params': {"Id": str(key_id).rstrip(),
                       "Pub": str(key_data['pub_key']).rstrip()}
        })
    return call_multi_contract(url, priv_key, token, data,
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

def new_users(url, priv_key, token, keys_data, ecosystem_id=1,
             verify_cert=True, wait_tx=True, timeout_secs=20,
             max_tries=20, gap_secs=1):
    data = []
    for pub_key, key_data in keys_data.items():
        data.append({
            'contract': 'NewUser',
            'params': {"NewPubkey": pub_key},
        })
    return call_multi_contract(url, priv_key, token, data,
                         ecosystem_id=ecosystem_id, verify_cert=verify_cert,
                         wait_tx=wait_tx, timeout_secs=timeout_secs,
                         max_tries=max_tries, gap_secs=gap_secs)

### Update Keys #### end ####
