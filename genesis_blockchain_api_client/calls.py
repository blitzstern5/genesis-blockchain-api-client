import requests
from requests_toolbelt.utils import dump
import logging
from time import sleep, time
from json import JSONDecodeError

from genesis_blockchain_tools import crypto

from .utils import dump_resp
from .errors import (
    get_error_by_id, NotResponseError, EmptyPublicKeyError, BadSignatureError,
    ServerError, UnknownError, errmsg_to_string,
    TxStatusHasErrmsgError, TxStatusBlockIDIsEmptyError,
    TxStatusNoBlockIDKeyError, WaitTxStatusTimeoutError,
    WaitTxStatusMaxTriesExceededError
)

from .blockchain.block import Block
from .blockchain.block_set import BlockSet

logger = logging.getLogger(__name__)

GENESIS_COMMON_ROLE_ID    = APLA_COMMON_ROLE_ID    = 0
GENESIS_ADMIN_ROLE_ID     = APLA_ADMIN_ROLE_ID     = 1
GENESIS_DEVELOPER_ROLE_ID = APLA_DEVELOPER_ROLE_ID = 2
GENESIS_CONSENSUS_ROLE_ID = APLA_CONSENSUS_ROLE_ID = 3
GENESIS_CANDIADATE_FOR_VALIDATORS_ROLE_ID = \
             APLA_CANDIADATE_FOR_VALIDATORS_ROLE_ID= 4
GENESIS_VALIDATOR_ROLE_ID = APLA_VALIDATOR_ROLE_ID = 5
GENESIS_INVESTOR_WITH_VOTING_RIGHTS_ROLE_ID = \
          APLA_INVESTOR_WITH_VOTING_RIGHTS_ROLE_ID = 6
GENESIS_DELEGATE_ROLE_ID  = APLA_DELEGATE_ROLE_ID  = 7

def raise_resp_error(resp, do_resp_dump=True):
    logger.debug("type(resp): % resp: %s" % (type(resp), resp))
    try:
        resp_json = resp.json()
        has_json = True
    except JSONDecodeError as e:
        has_json = False
    if has_json:
        msg = str(resp_json.get('msg', None))
        error_id = resp_json.get('error', None)
        logger.debug("error_id: %s" % error_id)
        error = get_error_by_id(error_id, msg=msg)
        if do_resp_dump:
            msg += ' ::: ' + str(dump_resp(resp))
        raise error(msg, error_id, response=resp)
    else:
        if resp.status_code != requests.codes.ok:
            logger.debug("bad response status code: %d" % resp.status_code)
            resp.raise_for_status()
        else:
            raise JSONDecodeError(dump_resp(resp))

def check_resp_error(resp, do_resp_dump=True, catch_errmsg=True):
    if not isinstance(resp, requests.Response):
        raise NotResponseError(type(resp))
    if resp.status_code != requests.codes.ok:
        raise_resp_error(resp, do_resp_dump=do_resp_dump)

def common_get_request(url, params={}, headers={}, verify_cert=True, 
                       catch_errmsg=True):
    resp = requests.get(url, headers=headers, params=params, verify=verify_cert)
    check_resp_error(resp, catch_errmsg=catch_errmsg)
    result = resp.json()
    logger.debug("url: %s; params: %s; headers: %s; result: %s" \
                 % (url, params, headers, result))
    return result

def common_post_request(url, params={}, data={}, headers={}, verify_cert=True,
                        catch_errmsg=True):
    resp = requests.post(url, headers=headers, params=params, data=data,
                         verify=verify_cert)
    check_resp_error(resp)
    result = resp.json()
    logger.debug("url: %s; params: %s; headers: %s; data: %s result: %s" \
                 % (url, params, headers, data, result))
    return result

def files_post_request(url, params={}, data={}, headers={}, verify_cert=True,
                        catch_errmsg=True):
    resp = requests.post(url, headers=headers, params=params, files=data,
                         verify=verify_cert)
    check_resp_error(resp)
    result = resp.json()
    logger.debug("url: %s; params: %s; headers: %s; data: %s result: %s" \
                 % (url, params, headers, data, result))
    return result

def get_uid(url, verify_cert=True):
    result = common_get_request(url + '/getuid', verify_cert=verify_cert)
    return result['uid'], result['token']

def get_network_info(url, verify_cert=True):
    result = common_get_request(url + '/network', verify_cert=verify_cert)
    if 'network_ud' in result:
        network_id = result['network_ud']
        result.pop('network_ud')
        result['network_id'] = network_id
    return result

def signtest(url, forsign, priv_key, verify_cert=True):
    result = common_post_request(
        url + '/signtest',
        data={'forsign': forsign, 'private': priv_key},
        verify_cert=verify_cert
    )
    return result['signature'], result['pubkey']

def sign_or_signtest(url, priv_key, data, sign_fmt='DER', use_signtest=False,
                     verify_cert=True, crypto_backend=crypto,
                     pub_key_fmt='04'):
    logger.debug("use_signtest: %s" % use_signtest)
    if use_signtest:
        logger.debug("running /signtest")
        signature, pub_key = signtest(url, data, priv_key,
                                      verify_cert=verify_cert) 
    else:
        signature = crypto_backend.sign(priv_key, data, sign_fmt=sign_fmt)
        pub_key = crypto_backend.get_public_key(priv_key, fmt=pub_key_fmt)
    return signature, pub_key

def login(url, priv_key, uid, token, sign_fmt='DER', use_signtest=False,
          verify_cert=True, crypto_backend=crypto, sign_tries=1, role_id=None,
          use_login_prefix=True, pub_key_fmt='04', ecosystem_id=None,
          network_id=None, auto_network_id=True):
    if auto_network_id:
        use_login_prefix = True
        network_info = get_network_info(url, verify_cert=verify_cert)
        if 'network_id' in network_info:
            network_id = network_info['network_id']
        else:
            network_id = None
    if use_login_prefix:
        if network_id:
            s_data = "LOGIN" + network_id + uid
        else:
            s_data = "LOGIN" + uid
    else:
        s_data = uid
    result = None
    for i in range(0, sign_tries):
        signature, pub_key = sign_or_signtest(url, priv_key, s_data,
                                              sign_fmt=sign_fmt,
                                              use_signtest=use_signtest,
                                              verify_cert=verify_cert,
                                              crypto_backend=crypto_backend,
                                              pub_key_fmt=pub_key_fmt)
        logger.debug("use_signtest: %s pub_key: %s, signature: %s" \
                     % (use_signtest, pub_key, signature)) 
        data={'pubkey': pub_key, 'signature': signature}
        if not ecosystem_id is None:
            data['ecosystem'] = ecosystem_id
        if not role_id is None:
            data['role_id'] = role_id
        try:
            result = common_post_request(
                url + '/login',
                headers={'Authorization': 'Bearer ' + token},
                data=data,
                verify_cert=verify_cert
            )
            result.update({'pub_key': pub_key, 'signature': signature})
            break
        except BadSignatureError as e:
            logger.debug("try %d, bad signature error: %s" % (i, e))
            raise e
        except Exception as e:
            logger.debug("try %d, some error: %s" % (i, e))
            raise e
    return result

def prepare_tx(url, priv_key, entity, token, data, use_signtest=False,
               verify_cert=True, sign_fmt='DER', crypto_backend=crypto,
               pub_key_fmt='04'):
    result = common_post_request(
        url + '/prepare/' + entity,
        headers={'Authorization': 'Bearer ' + token},
        data=data,
        verify_cert=verify_cert
    )
    signature, pub_key = sign_or_signtest(url, priv_key, result['forsign'],
                                          sign_fmt=sign_fmt,
                                          use_signtest=use_signtest,
                                          verify_cert=verify_cert,
                                          crypto_backend=crypto_backend,
                                          pub_key_fmt=pub_key_fmt)
    logger.debug("use_signtest: %s pub_key: %s, signature: %s" \
                     % (use_signtest, pub_key, signature)) 
    result.update({'signature': signature})
    return result


def call_contract(url, pub_key, token, time, signature, 
                  name='', use_request_id=True, 
                  data='', verify_cert=True, send_pub_key=True):
    data2 = {'time': time, 'signature': signature}
    if send_pub_key:
        data2.update({'pubkey': pub_key})
    if use_request_id:
        data = data2
    else:
        if data:
            data.update(data2)
        else:
            data = data2
    result = common_post_request(
        url + '/contract/' + name,
        headers={'Authorization': 'Bearer ' + token},
        data=data,
        verify_cert=verify_cert
    )
    return result


def get_tx_status(url, tx_hash, token, verify_cert=True):
    logger.debug("    requesting /txstatus/%s ..." % tx_hash)
    result = common_get_request(
        url + '/txstatus/' + tx_hash,
        headers={'Authorization': 'Bearer ' + token},
        verify_cert=verify_cert
    )
    logger.debug("result: %s" % result)
    if 'errmsg' in result:
        logger.debug("    'errmsg' key is present HEREEEEE!!!!")
        raise TxStatusHasErrmsgError(errmsg_to_string(result['errmsg']),
                    url=url, tx_hash=tx_hash, token=token,
                    verify_cert=verify_cert, result=result)

    if 'blockid' in result:
        logger.debug("    'blockid' key is present")
        if not result['blockid']:
            logger.debug("'blockid' is empty")
            raise TxStatusBlockIDIsEmptyError("blockid is EMPTY", url=url,
                    tx_hash=tx_hash, token=token, verify_cert=verify_cert,
                    result=result)
    else:
        logger.debug("    'blockid' key is absent")
        raise TxStatusNoBlockIDKeyError("'blockid key is absent", url=url,
                tx_hash=tx_hash, token=token, verify_cert=verify_cert,
                result=result)
    return result


def wait_tx_status(url, tx_hash, token, timeout_secs=100, max_tries=100,
                   gap_secs=1, show_indicator=True, verify_cert=True):

    logger.debug("gap_secs: %d timeout_secs: %d max_tries: %d" %(gap_secs,
        timeout_secs, max_tries))
    end_time = time() + timeout_secs
    result = None
    cnt=1
    while True:
        if show_indicator:
            print("Waiting (%d seconds) for the completion of the transaction (try %d/%d) ..." % (timeout_secs, cnt, max_tries))
        logger.debug("try %d", cnt)
        no_block_id = False
        try:
            result = get_tx_status(url, tx_hash, token, verify_cert=verify_cert)
            return result
        except TxStatusNoBlockIDKeyError as e: 
            no_block_id = True
        except TxStatusBlockIDIsEmptyError as e:
            no_block_id = True

        logger.debug("no_block_id: %s" % no_block_id)

        if time() > end_time:
            logger.debug("time exceeded")
            raise WaitTxStatusTimeoutError("time exceeded", url=url,
                    tx_hash=tx_hash,
                    token=token,
                    verify_cert=verify_cert, result=result,
                    timeout_secs=timeout_secs, max_tries=max_tries,
                    gap_secs=gap_secs, tx_status_error=e)
        if cnt > max_tries:
            logger.debug("max tries exceeded")
            raise WaitTxStatusMaxTriesExceededError("max tries exceeded",
                    url=url,
                    tx_hash=tx_hash,
                    token=token, verify_cert=verify_cert, result=result,
                    timeout_secs=timeout_secs, max_tries=max_tries,
                    gap_secs=gap_secs, tx_status_error=e)
        cnt += 1
        sleep(gap_secs)

def get_version(url, verify_cert=True):
    result = common_get_request(url + '/version', verify_cert=verify_cert)
    return result

def get_max_block_id(url, verify_cert=True):
    result = common_get_request(url + '/maxblockid', verify_cert=verify_cert)
    return result['max_block_id']

def get_block_metadata(url, block_id, verify_cert=True):
    result = common_get_request("%s/block/%s" % (url, block_id),
                                verify_cert=verify_cert)
    return result


def get_blocks_data(url, block_id, count=None, verify_cert=True):
    params = {'block_id': block_id, 'verify_cert': verify_cert}
    if count:
        params.update(count=count)
    return common_get_request(url + '/blocks', params=params,
                              verify_cert=verify_cert)

def get_block_data(url, block_id, verify_cert=True):
    d = get_blocks_data(url, block_id, count=1, verify_cert=verify_cert)
    return d[str(block_id)] if d else None


def get_detailed_blocks_data(url, block_id, count=None, verify_cert=True):
    params = {'block_id': block_id}
    if count:
        params.update(count=count)
    return common_get_request(url + '/detailed_blocks', params=params,
                              verify_cert=verify_cert)

def get_detailed_block_data(url, block_id, verify_cert=True):
    d = get_detailed_blocks_data(url, block_id, count=1, verify_cert=verify_cert)
    return d[str(block_id)] if d else None


def get_blocks(url, block_id, count=None, verify_cert=True, b64decode_hashes=True):
    return BlockSet(from_dict=get_blocks_data(url, block_id, count=count, verify_cert=verify_cert), b64decode_hashes=b64decode_hashes)


def get_block(url, block_id, verify_cert=True, b64decode_hashes=True):
    b = Block(from_dict=get_blocks_data(url, block_id, count=1, verify_cert=verify_cert), b64decode_hashes=b64decode_hashes)
    return b


def get_detailed_blocks(url, block_id, count=None, verify_cert=True, b64decode_hashes=True):
    return BlockSet(from_detailed_dict=get_detailed_blocks_data(url, block_id, count=count, verify_cert=verify_cert), b64decode_hashes=b64decode_hashes)


def get_detailed_block(url, block_id, verify_cert=True, b64decode_hashes=True):
    b = Block(from_detailed_dict=get_detailed_blocks_data(url, block_id, count=1, verify_cert=verify_cert), b64decode_hashes=b64decode_hashes)
    return b

