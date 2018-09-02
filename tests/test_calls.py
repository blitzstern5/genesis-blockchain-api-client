import os
import json
import time
import re
import unittest
import requests
from requests import Response
import logging

from pprint import pprint

from urllib.parse import urlparse
from mock import patch
from nose import with_setup

from genesis_blockchain_tools.crypto.backend import (
    import_crypto_by_backend,
)

from genesis_blockchain_api_client.calls import (
    requests, get_uid, signtest, sign_or_signtest, login, prepare_tx,
    call_contract, get_tx_status, wait_tx_status,
    TxStatusHasErrmsgError,
    TxStatusNoBlockIDKeyError,
    TxStatusBlockIDIsEmptyError,
    get_max_block_id, get_blocks_data, get_block_data, get_version,
    get_blocks, get_block, get_block_metadata,
)
from genesis_blockchain_api_client.errors import (
    get_error_by_id, EmptyPublicKeyError, BadSignatureError, ServerError,
)
from genesis_blockchain_api_client.logging import setup_logging
from genesis_blockchain_api_client.utils import dump_resp
from genesis_blockchain_api_client.blockchain.block import Block
from genesis_blockchain_api_client.blockchain.block_set import BlockSet
from .utils import is_number, is_string, save_keypair_as, save_signature_as

use_mock = True 
use_mock = False
g_patcher, p_patcher = None, None
pub_key, uid = None, None
api_root_url = 'http://127.0.0.1:17301/api/v2'
logger = logging.getLogger(__name__)
setup_logging()
basedir = os.path.abspath(os.path.dirname(__file__))
crypto = import_crypto_by_backend('cryptography')

verify_cert = True

from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

#backend_version = '201802XX'
#backend_version = '201806XX'
#backend_version = '20180830'
backend_version = get_latest_version()
#print("backend version: %s" % backend_version)
for option_name, option_value in version_to_options(backend_version).items():
    #print("backend option: %s='%s'" % (option_name, option_value))
    globals()[option_name] = option_value

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

def mocked_requests_get(*args, **kwargs):
    if args[0] == 'http://someurl.com/test.json':
        return MockResponse({"key1": "value1"}, 200)
    elif args[0] == 'http://someotherurl.com/anothertest.json':
        return MockResponse({"key2": "value2"}, 200)
    else:
        parsed_url = urlparse(args[0])
        resource_file = os.path.normpath('tests/resources%s' % parsed_url.path)
        data = open(resource_file, mode='rb').read().decode('utf-8')
        data = json.loads(data)
        obj = MockResponse(data, 200)
        logger.debug("mock get data: %s" % data)
        return obj
    return MockResponse(None, 404)

def mocked_requests_post(*args, **kwargs):
    if args[0] == 'http://someurl.com/test.json':
        return MockResponse({"key1": "value1"}, 200)
    elif args[0] == 'http://someotherurl.com/anothertest.json':
        return MockResponse({"key2": "value2"}, 200)
    else:
        parsed_url = urlparse(args[0])
        logging.debug("parsed_url.path: %s" % parsed_url.path)
        resource_file = os.path.normpath('tests/resources%s' % parsed_url.path)
        logging.debug("resource_file: %s" % resource_file)
        data = open(resource_file, mode='rb').read().decode('utf-8')
        logger.debug("loaded data: %s" % data)
        data = json.loads(data)
        #entrypoint = parsed_url.path.split('/')[-1]
        words = ('login', 'contract')
        m = re.search("\/("+'|'.join(words)+")(\/([a-zA-Z0-9\-\_\,\.]+)?)?$",
                      parsed_url.path)
        if m:
            logger.debug("m.group(1): %s" % m.group(1))
            logger.debug("m.group(2): %s" % m.group(2))
            logger.debug("m.group(3): %s" % m.group(3))
            if m.group(1) == 'login':
                logger.debug("login case, pub_key: %s" % pub_key)
                data['pub_key'] = pub_key 
            elif m.group(1) == 'contract':
                data['pub_key'] = pub_key 
                request_id = m.group(3)
                logger.debug("contract case, pub_key: %s, request_id: %s" \
                             % (pub_key, request_id))
                resource_file = os.path.normpath('tests/resources%s' % parsed_url.path)
        logger.debug("parsed to json data: %s" % data)
        obj = MockResponse(data, 200)
        logger.debug("mock post data: %s" % data)
        return obj
    return MockResponse(None, 404)

def mocked_sign(*args, **kwargs):
    logger.debug("started")
    return '3046022100f9f4fdc211c58ddda1921d21e039cfda2fd566c4b90d3b709e010175bda6b706022100ec03cf485c9da8cc074699154b80a830f639c0239282e3d563a669cde7627967'

def fake_urllib_urlparse(url):
    parsed_url = urlparse(url)
    resource_file = os.path.normpath('tests/resources%s' % parsed_url.path)
    return open(resource_file, mode='rb')

def my_setup():
    if not use_mock:
        return
    global g_patcher, p_patcher
    g_patcher = patch('genesis_blockchain_api_client.api_calls.requests.get',
                      side_effect=mocked_requests_get)
    p_patcher = patch('genesis_blockchain_api_client.api_calls.requests.post',
                      side_effect=mocked_requests_post)
    g_patcher.start()
    p_patcher.start()

def my_teardown():
    if not use_mock:
        return
    global g_patcher, p_patcher
    p_patcher.stop()
    g_patcher.stop()

@with_setup(my_setup, my_teardown)
def test_get_uid():
    result = get_uid(api_root_url)
    assert type(result) == tuple and len(result) == 2
    assert is_number(result[0])
    assert is_string(result[1])
    if use_mock:
        assert result[0] == '3584828363455824320'
        assert result[1] == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIzNTg0ODI4MzYzNDU1ODI0MzIwIiwiZXhwIjoxNTI3MzA5ODY5fQ.1x1oPw_1RpeUcJBM7FwTdT05CflnhECAYwT14oJZzUQ'

#@with_setup(my_setup, my_teardown)
#def test_signtest():
#    forsign = "Some data for sign"
#    priv_key = crypto.gen_private_key()
#    result = signtest(api_root_url, forsign, priv_key)
#    assert type(result) == tuple and len(result) == 2
#    assert is_string(result[0])
#    assert is_string(result[1])
#    if use_mock:
#        assert result[0] == 'df921217c1ac7e0f148f7ecec19659af830e09bfe7edf09b6d313fad3f8529194aeda2d8189c2f4e20b2744652663983fee992cb01ba9c7ff3b1d33d458a5103'
#        assert result[1] == '45dc2d1acb63fd25a4b51c81d076a896d89e61ae14b7ce1e2cf02f6de6976ffe16fe1ac6b96b42cb2ab77c0254023393e3164244e47b7a65c6ba8c16f2545507'

@with_setup(my_setup, my_teardown)
def test_login():
    global pub_key
    uid, token = get_uid(api_root_url)
    if use_mock:
        uid = '3584828363455824320'
        priv_key = 'c36f377efc867914daa998eaadf6722dc28fe7a4c239a251220d5d7055c4aadd'
        pub_key = crypto.get_public_key(priv_key)
    else:
        priv_key = crypto.gen_private_key()

    try:
        result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                       use_signtest=use_signtest, crypto_backend=crypto,
                       use_login_prefix=use_login_prefix,
                       pub_key_fmt=pub_key_fmt)
    except BadSignatureError as e:
        if not use_mock:
            save_signature_as(priv_key, e.request_signature, crypto, "bad")
        raise e
    #except ServerError as e:
    #    logger.debug("dump ServerError.response: %s" % dump_resp(e.response))
    #    raise e
    if not use_mock:
        save_signature_as(priv_key, result['signature'], crypto, "good")

    assert type(result) == dict
    keys = ['token', 'refresh', 'ecosystem_id', 'key_id', 'address',
            'notify_key', 'timestamp']
    for key in keys:
        assert key in result
        if key in ['ecosystem_id', 'timestamp', 'key_id']:
            assert is_number(result[key])
        elif key in ['token', 'refresh', 'address', 'pub_key']:
            assert is_string(result[key])
    if use_mock:
        kv = {'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlY29zeXN0ZW1faWQiOiIxIiwia2V5X2lkIjoiODQ0MTQxNDI5NzY4MDI3MTA5OSIsInJvbGVfaWQiOiIwIiwiaXNfbW9iaWxlIjoiMCIsImV4cCI6MTUyNzYzMDE3Nn0.F1PdWTgLoiK1GyiFtOcrhOlmuSdnju8PXewaf5nHyP0', 'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlY29zeXN0ZW1faWQiOiIxIiwia2V5X2lkIjoiODQ0MTQxNDI5NzY4MDI3MTA5OSIsInJvbGVfaWQiOiIwIiwiaXNfbW9iaWxlIjoiMCIsImV4cCI6MTUzMDE4NjE3Nn0.P6heXrB2HEli8BWpKzIleyfJVtqhAH01ujTCpWcIdHs', 'ecosystem_id': '1', 'key_id': '8441414297680271099', 'address': '0844-1414-2976-8027-1099', 'notify_key': '7ea3b6835cd86acf5c8321983fd8df466ff425288e2eccd8fe2e67744d6c3171', 'timestamp': '1527594176', 'pub_key': pub_key}
        for key, value in kv.items():
            assert key in result
            logging.debug("key: %s, exp value: %s, act value: %s" % (key, value, result[key]))
            assert value == result[key]

@with_setup(my_setup, my_teardown)
def test_prepare_tx():
    global pub_key
    uid, token = get_uid(api_root_url)
    if use_mock:
        uid = '3584828363455824320'
        priv_key = 'c36f377efc867914daa998eaadf6722dc28fe7a4c239a251220d5d7055c4aadd'
        pub_key = crypto.get_public_key(priv_key)
    else:
        priv_key = crypto.gen_private_key()

    try:
        l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                         use_signtest=use_signtest, crypto_backend=crypto,
                         use_login_prefix=use_login_prefix,
                         pub_key_fmt=pub_key_fmt)
    except BadSignatureError as e:
        if not use_mock:
            save_signature_as(priv_key, e.request_signature, crypto, "bad")
        raise e
    if not use_mock:
        save_signature_as(priv_key, l_result['signature'], crypto, "good")

    entity = 'MainCondition'
    token = l_result['token']
    data = "Some data"
    p_result = prepare_tx(api_root_url, priv_key, entity, token, data,
                          use_signtest=use_signtest, verify_cert=verify_cert,
                          sign_fmt=sign_fmt, crypto_backend=crypto,
                          pub_key_fmt=pub_key_fmt)
    if use_request_id:
        keys = ['request_id', 'forsign', 'signs', 'values', 'time',
            'signature']
    else:
        keys = ['forsign', 'signs', 'values', 'time',
            'signature']

    for key in keys:
        assert key in p_result
        if key in ['time']:
            assert is_number(p_result[key])
        elif key in ['request_id', 'forsign', 'signature']:
            assert is_string(p_result[key])
    if use_mock:
        kv = {'request_id': 'e7fdd221-b68c-43b7-9ec7-03fce40ae453', 'forsign': 'e7fdd221-b68c-43b7-9ec7-03fce40ae453,261,1527680210,-1064602072687537418,1,0,,,0', 'signs': None, 'values': None, 'time': '1527680210', 'signature': '3046022100f9f4fdc211c58ddda1921d21e039cfda2fd566c4b90d3b709e010175bda6b706022100ec03cf485c9da8cc074699154b80a830f639c0239282e3d563a669cde7627967'}
        for key, value in kv.items():
            assert key in p_result
            logging.debug("key: %s, exp value: %s, act value: %s" % (key, value, p_result[key]))
            if key == 'signature':
                continue
            assert value == p_result[key]
    logger.debug("p_result: %s" % p_result)

@with_setup(my_setup, my_teardown)
def test_call_contract():
    global pub_key
    uid, token = get_uid(api_root_url)
    if use_mock:
        uid = '3584828363455824320'
        priv_key = 'c36f377efc867914daa998eaadf6722dc28fe7a4c239a251220d5d7055c4aadd'
    else:
        priv_key = crypto.gen_private_key()
    logger.debug("PRIV_KEY: %s" % priv_key)
    pub_key = crypto.get_public_key(priv_key)
    try:
        l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                         use_signtest=use_signtest, crypto_backend=crypto,
                         use_login_prefix=use_login_prefix,
                         pub_key_fmt=pub_key_fmt)
    except BadSignatureError as e:
        if not use_mock:
            save_signature_as(priv_key, e.request_signature, crypto, "bad")
        raise e
    if not use_mock:
        save_signature_as(priv_key, l_result['signature'], crypto, "good")
    entity = 'MainCondition'
    token = l_result['token']
    data = ''
    pub_key = crypto.get_public_key(priv_key)
    p_result = prepare_tx(api_root_url, priv_key, entity, token, data,
                          use_signtest=use_signtest, verify_cert=verify_cert,
                          sign_fmt=sign_fmt, crypto_backend=crypto,
                          pub_key_fmt=pub_key_fmt)
    logger.debug("p_result: %s" % p_result)
    if use_request_id:
        name = p_result.get('request_id', None)
        data = ''
    else:
        name = entity
    try:
        c_result = call_contract(api_root_url, pub_key, token,
                                 p_result['time'], p_result['signature'], 
                                 name=name, use_request_id=use_request_id, 
                                 data=data)
        assert 'hash' in c_result
        logger.debug("hash: %s" % c_result['hash'])
    except EmptyPublicKeyError as e:
        if not use_mock:
            save_keypair_as(priv_key, pub_key, crypto, "bad")
        raise e
    if not use_mock:
        save_keypair_as(priv_key, pub_key, crypto, "good")
    logger.debug("c_result: %s" % c_result)

@with_setup(my_setup, my_teardown)
def test_get_tx_status():
    global pub_key
    uid, token = get_uid(api_root_url)
    if use_mock:
        uid = '3584828363455824320'
        priv_key = 'c36f377efc867914daa998eaadf6722dc28fe7a4c239a251220d5d7055c4aadd'
    else:
        priv_key = crypto.gen_private_key()
    logger.debug("PRIV_KEY: %s" % priv_key)
    pub_key = crypto.get_public_key(priv_key)
    try:
        l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                         use_signtest=use_signtest, crypto_backend=crypto,
                         use_login_prefix=use_login_prefix,
                         pub_key_fmt=pub_key_fmt)
    except BadSignatureError as e:
        if not use_mock:
            save_signature_as(priv_key, e.request_signature, crypto, "bad")
        raise e
    if not use_mock:
        save_signature_as(priv_key, l_result['signature'], crypto, "good")
    entity = 'MainCondition'
    token = l_result['token']
    data = ''
    pub_key = crypto.get_public_key(priv_key)
    p_result = prepare_tx(api_root_url, priv_key, entity, token, data,
                          use_signtest=use_signtest, verify_cert=verify_cert,
                          sign_fmt=sign_fmt, crypto_backend=crypto,
                          pub_key_fmt=pub_key_fmt)
    logger.debug("p_result: %s" % p_result)
    if use_request_id:
        name = p_result.get('request_id', None)
        data = ''
    else:
        name = entity
    try:
        c_result = call_contract(api_root_url, pub_key, token,
                                 p_result['time'], p_result['signature'], 
                                 name=name, use_request_id=use_request_id, 
                                 data=data)
        assert 'hash' in c_result
        logger.debug("hash: %s" % c_result['hash'])
    except EmptyPublicKeyError as e:
        if not use_mock:
            save_keypair_as(priv_key, pub_key, crypto, "bad")
        raise e
    if not use_mock:
        save_keypair_as(priv_key, pub_key, crypto, "good")
    logger.debug("c_result: %s" % c_result)
    
    blockid_is_empty_catched = False
    try:
        s_result = get_tx_status(api_root_url, c_result['hash'], token,
                             verify_cert=True)
    except TxStatusBlockIDIsEmptyError as e:
        blockid_is_empty_catched = True 
    assert blockid_is_empty_catched

    time.sleep(2)

    errmsg_catched = False
    no_block_id = False
    try:
        s_result = get_tx_status(api_root_url, c_result['hash'], token,
                             verify_cert=True)
    except TxStatusNoBlockIDKeyError as e:
        no_block_id = True
    except TxStatusBlockIDIsEmptyError as e:
        no_block_id = True
    except TxStatusHasErrmsgError as e:
        errmsg_catched = True 
    assert no_block_id or errmsg_catched

@with_setup(my_setup, my_teardown)
def test_wait_tx_status():
    global pub_key
    uid, token = get_uid(api_root_url)
    if use_mock:
        uid = '3584828363455824320'
        priv_key = 'c36f377efc867914daa998eaadf6722dc28fe7a4c239a251220d5d7055c4aadd'
    else:
        priv_key = crypto.gen_private_key()
    logger.debug("PRIV_KEY: %s" % priv_key)
    pub_key = crypto.get_public_key(priv_key)
    try:
        l_result = login(api_root_url, priv_key, uid, token, sign_fmt=sign_fmt,
                         use_signtest=use_signtest, crypto_backend=crypto,
                         use_login_prefix=use_login_prefix,
                         pub_key_fmt=pub_key_fmt)
    except BadSignatureError as e:
        if not use_mock:
            save_signature_as(priv_key, e.request_signature, crypto, "bad")
        raise e
    if not use_mock:
        save_signature_as(priv_key, l_result['signature'], crypto, "good")
    entity = 'MainCondition'
    token = l_result['token']
    data = ''
    pub_key = crypto.get_public_key(priv_key)
    p_result = prepare_tx(api_root_url, priv_key, entity, token, data,
                          use_signtest=use_signtest, verify_cert=verify_cert,
                          sign_fmt=sign_fmt, crypto_backend=crypto,
                          pub_key_fmt=pub_key_fmt)
    logger.debug("p_result: %s" % p_result)
    if use_request_id:
        name = p_result.get('request_id', None)
        data = ''
    else:
        name = entity
    try:
        c_result = call_contract(api_root_url, pub_key, token,
                                 p_result['time'], p_result['signature'], 
                                 name=name, use_request_id=use_request_id, 
                                 data=data)
        assert 'hash' in c_result
        logger.debug("hash: %s" % c_result['hash'])
    except EmptyPublicKeyError as e:
        if not use_mock:
            save_keypair_as(priv_key, pub_key, crypto, "bad")
        raise e
    if not use_mock:
        save_keypair_as(priv_key, pub_key, crypto, "good")
    logger.debug("c_result: %s" % c_result)
    
    errmsg_catched = False
    try:
        w_result = wait_tx_status(api_root_url, c_result['hash'], token,
                                  timeout_secs=100, max_tries=100,
                                  #gap_secs=0.05,
                                  gap_secs=1,
                                  verify_cert=verify_cert)
    except TxStatusHasErrmsgError as e:
        logger.debug("errmsg is present: OK")
        errmsg_catched = True 
    except Exception as e:
        logger.debug("UNKONWN error: %s" % e)
        raise e
    #assert errmsg_catched

@with_setup(my_setup, my_teardown)
def test_get_version():
    result = get_version(api_root_url)
    assert is_string(result)

@with_setup(my_setup, my_teardown)
def test_get_max_block_id():
    result = get_max_block_id(api_root_url)
    assert is_number(result)

@with_setup(my_setup, my_teardown)
def test_get_block_metadata():
    block_id = 1
    result = get_block_metadata(api_root_url, block_id)
    assert type(result) == dict
    keys = ('hash', 'ecosystem_id', 'key_id', 'time', 'tx_count',
            'rollbacks_hash')
    for key in keys:
        assert key in result
        if key in ('hash', 'rollbacks_hash'):
            assert is_string(result[key])
        if key in ('ecosystem_id', 'time', 'key_id', 'tx_count'):
            assert is_number(result[key])

@with_setup(my_setup, my_teardown)
def test_get_blocks_data():
    block_id = 1
    max_count = 3
    for count in range(1, max_count):
        result = get_blocks_data(api_root_url, block_id, count=count)
        assert type(result) == dict
        assert len(result) == count

@with_setup(my_setup, my_teardown)
def test_get_blocks():
    block_id = 1
    max_count = 3
    for count in range(1, max_count):
        result = get_blocks(api_root_url, block_id, count=count)
        assert isinstance(result, BlockSet)
        assert len(result.blocks) == count

@with_setup(my_setup, my_teardown)
def test_get_block_data():
    result = get_block_data(api_root_url, 1)
    assert type(result) == list or type(result) is None

@with_setup(my_setup, my_teardown)
def test_get_block():
    block_id = 1
    result = get_block(api_root_url, block_id)
    print("type(result): %s" % type(result))
    assert isinstance(result, Block)

