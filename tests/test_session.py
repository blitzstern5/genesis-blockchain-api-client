import logging

from genesis_blockchain_tools import crypto

from genesis_blockchain_api_client.session import Session
from genesis_blockchain_api_client.calls import TxStatusHasErrmsgError
from genesis_blockchain_api_client.logging import setup_logging
from .utils import is_number, is_string, save_keypair_as, save_signature_as

from genesis_blockchain_api_client.blockchain.block import Block
from genesis_blockchain_api_client.blockchain.block_set import BlockSet

from nose import with_setup

api_root_url = 'http://127.0.0.1:17301/api/v2'
logger = logging.getLogger(__name__)
setup_logging()

verify_cert = True

from genesis_blockchain_api_client.backend.versions import (
    version_to_options, get_latest_version
)

use_backend_version = True
#backend_version = '201802XX'
#backend_version = '201806XX'
#backend_version = '20180830'
backend_version = get_latest_version()
#print("backend version: %s" % backend_version)
for option_name, option_value in version_to_options(backend_version).items():
    #print("backend option: %s='%s'" % (option_name, option_value))
    globals()[option_name] = option_value

def my_setup():
    pass

def my_teardown():
    pass

def create_session(use_backend_version):
    if use_backend_version:
        sess = Session(api_root_url, backend_version=backend_version)
    else:
        sess = Session(api_root_url, use_login_prefix=use_login_prefix,
                   use_signtest=use_signtest,
                   sign_fmt=sign_fmt,
                   pub_key_fmt=pub_key_fmt,
                   use_request_id=use_request_id,
                   verify_cert=verify_cert)
    return sess

@with_setup(my_setup, my_teardown)
def test_init():
    sess = create_session(use_backend_version)
    assert sess.api_url == api_root_url
    assert sess.verify_cert == verify_cert
    assert sess.priv_key == None
    assert sess.pub_key == None
    assert sess.sign_fmt == sign_fmt
    assert sess.use_signtest == use_signtest
    assert sess.crypto_backend == crypto
    assert sess.pub_key_fmt == pub_key_fmt
    assert sess.send_pub_key == True
    assert sess.max_sign_tries == 1
    assert sess.use_login_prefix == True
    assert sess.uid == None
    assert sess.token == None

@with_setup(my_setup, my_teardown)
def test_get_uid():
    sess = create_session(use_backend_version)
    assert not sess.uid
    assert not sess.token
    sess.get_uid()
    assert sess.uid and len(sess.uid) > 10
    assert sess.token and len(sess.token) > 10

@with_setup(my_setup, my_teardown)
def test_gen_keypair():
    sess = create_session(use_backend_version)
    assert not sess.priv_key
    assert not sess.pub_key
    sess.gen_keypair()
    assert sess.priv_key and len(sess.priv_key) == 64
    assert sess.pub_key and len(sess.pub_key) == 128

@with_setup(my_setup, my_teardown)
def test_login():
    sess = create_session(use_backend_version)
    assert not sess.uid
    assert not sess.token
    assert not sess.priv_key
    assert not sess.pub_key
    assert not sess.l_result
    sess.gen_keypair()
    sess.login()
    assert sess.uid and len(sess.uid) > 10
    assert sess.token and len(sess.token) > 10
    assert sess.priv_key and len(sess.priv_key) == 64
    assert sess.pub_key and len(sess.pub_key) == 128
    assert sess.l_result and type(sess.l_result) == dict
    assert 'token' in sess.l_result and len(sess.l_result['token']) > 100
    assert 'refresh' in sess.l_result and len(sess.l_result['refresh']) > 100

@with_setup(my_setup, my_teardown)
def test_prepare_tx():
    sess = create_session(use_backend_version)
    assert not sess.p_result
    sess.gen_keypair()
    sess.login()
    sess.prepare_tx(name='MainCondition')
    assert sess.p_result and type(sess.p_result) == dict
    assert 'request_id' in sess.p_result \
            and len(sess.p_result['request_id']) > 20
    assert 'forsign' in sess.p_result \
            and len(sess.p_result['forsign']) > 36

@with_setup(my_setup, my_teardown)
def test_call_contract():
    sess = create_session(use_backend_version)
    assert not sess.c_result
    sess.gen_keypair()
    sess.login()
    sess.prepare_tx(name='MainCondition')
    sess.call_contract()
    assert sess.c_result and type(sess.c_result) == dict

@with_setup(my_setup, my_teardown)
def test_wait_tx_status():
    sess = create_session(use_backend_version)
    assert not sess.c_result
    sess.gen_keypair()
    sess.login()
    sess.prepare_tx(name='MainCondition')
    sess.call_contract()

    errmsg_catched = False
    try:
        sess.wait_tx_status()
    except TxStatusHasErrmsgError as e:
        errmsg_catched = True 
    assert errmsg_catched
    #assert sess.tx_status and type(sess.tx_status) == dict

@with_setup(my_setup, my_teardown)
def test_get_version():
    sess = create_session(use_backend_version)
    assert is_string(sess.get_version())

@with_setup(my_setup, my_teardown)
def test_get_max_block_id():
    sess = create_session(use_backend_version)
    assert is_number(sess.get_max_block_id())

@with_setup(my_setup, my_teardown)
def test_get_blocks_data():
    sess = create_session(use_backend_version)
    block_id = 1
    count = 1
    data = sess.get_blocks_data(block_id, count=1)
    assert type(data) == dict
    assert str(block_id) in data

    max_count = 4
    block_id = 1
    for count in range(1, max_count):
        data = sess.get_blocks_data(block_id, count=count)
        assert type(data) == dict
        assert str(block_id) in data
    assert len(data) == count

@with_setup(my_setup, my_teardown)
def test_get_block_data():
    sess = create_session(use_backend_version)
    block_id = 1
    data = sess.get_block_data(block_id)
    assert type(data) == list or type(data) is None


@with_setup(my_setup, my_teardown)
def test_get_detailed_blocks_data():
    sess = create_session(use_backend_version)
    block_id = 1
    count = 1
    data = sess.get_detailed_blocks_data(block_id, count=1)
    assert type(data) == dict
    assert str(block_id) in data

    max_count = 4
    block_id = 1
    for count in range(1, max_count):
        data = sess.get_detailed_blocks_data(block_id, count=count)
        assert type(data) == dict
        assert str(block_id) in data
    assert len(data) == count

@with_setup(my_setup, my_teardown)
def test_get_detailed_block_data():
    sess = create_session(use_backend_version)
    block_id = 1
    data = sess.get_detailed_block_data(block_id)
    assert type(data) == dict or type(data) is None


@with_setup(my_setup, my_teardown)
def test_get_blocks():
    sess = create_session(use_backend_version)
    block_id = 1
    count = 3
    blocks = sess.get_blocks(block_id, count=count)
    assert isinstance(blocks, BlockSet)
    assert len(blocks.blocks) == count

@with_setup(my_setup, my_teardown)
def test_get_block():
    sess = create_session(use_backend_version)
    block_id = 1
    result = sess.get_block_metadata(block_id)
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
def test_get_detailed_blocks():
    sess = create_session(use_backend_version)
    block_id = 1
    count = 3
    blocks = sess.get_detailed_blocks(block_id, count=count)
    assert isinstance(blocks, BlockSet)
    assert len(blocks.blocks) == count

@with_setup(my_setup, my_teardown)
def test_get_detailed_block():
    sess = create_session(use_backend_version)
    block_id = 1
    result = sess.get_detailed_block(block_id)
    assert isinstance(result, Block)
