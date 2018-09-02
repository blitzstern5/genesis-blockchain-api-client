from nose import with_setup

from genesis_blockchain_api_client.blockchain.tx_set import TxSet
from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_blockchain_api_client.blockchain.block.header import Header

from .blockchain_commons import d1, d3, get_txs

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_get_block_id_from_dict():
    assert get_block_id_from_dict(d1[0]) == '123'
    assert get_block_id_from_dict(d1[1]) == '456'

@with_setup(my_setup, my_teardown)
def test_get_block_id_from_dict():
    assert get_block_data_from_dict(d1[0]) == d1[0]['123']
    assert get_block_data_from_dict(d1[1]) == d1[1]['456']

@with_setup(my_setup, my_teardown)
def test_block_from_dict():
    b = d1[0]

    bl = Block()
    bl.from_dict(b)
    ts = get_txs(b)
    txs = TxSet(from_list=ts)
    assert bl.id == get_block_id_from_dict(b)
    assert isinstance(bl.tx_set, TxSet)

    i = 0
    while i < len(bl.tx_set.txs):
        for n in ('hash', 'contract_name', 'params', 'key_id'):
            assert getattr(bl.tx_set.txs[i], n) == getattr(txs.txs[i], n)
        i += 1

    bl = Block(from_dict=b)
    ts = get_txs(b)
    txs = TxSet(from_list=ts)
    assert bl.id == get_block_id_from_dict(b)
    assert isinstance(bl.tx_set, TxSet)

    i = 0
    while i < len(bl.tx_set.txs):
        for n in ('hash', 'contract_name', 'params', 'key_id'):
            assert getattr(bl.tx_set.txs[i], n) == getattr(txs.txs[i], n)
        i += 1

@with_setup(my_setup, my_teardown)
def test_block_from_detailed_dict():
    b = d3[0]

    bl = Block(b64decode_hashes=False)
    bl.from_detailed_dict(b)
    assert bl.id == get_block_id_from_dict(b)
    assert isinstance(bl.tx_set, TxSet)
    assert isinstance(bl.header, Header)
    assert bl.hash == '3JY6NL6KiuMGXgdzSmnHKPnhwZzAjFThiaHtkJekZdI='
    assert bl.ecosystem_id == 0
    assert bl.node_position == 0
    assert bl.tx_count == 2
    assert bl.key_id == -5953874702473585171
    assert bl.time == 1535819403
    assert bl.rollbacks_hash == 'leECi3/aNz4Hkk7AFUJ9bAjsdOYjGMY0+/ZpspzWgAI='
    assert bl.mrkl_root == 'N2U2NmMwNjkxMzc2NDAxYTA4ZGQ2YWUzMGMyMDVlOTgxYWI1OTYxMDRiYzcyMDhlOTM5NjI3ODVkYWE5ZDQ4Nw=='
    assert bl.bin_data == None
    assert bl.bin_data == None
    assert bl.sys_update == False
    assert bl.gen_block == False
    assert bl.stop_count == 0
    assert bl.header.block_id == '123'
    assert bl.header.time == 1535819403
    assert bl.header.ecosystem_id == 0
    assert bl.header.node_position == 0
    assert bl.header.sign == '6LVsJppg6jPGYv/wpfvz+/9+Cc44POXMWAFcOFB60BKT06tg7S2R4WEcxcWQmRVesyanT8y/5XETsnzOgBDMIA=='
    assert bl.header.hash == "kQPWd2asxbCDTuBZtAEDSNrV6emBb4ILLsvuTqRVoqc="
    assert bl.header.version == 1

    bl = Block(b64decode_hashes=True)
    bl.from_detailed_dict(b)
    assert bl.id == get_block_id_from_dict(b)
    assert isinstance(bl.tx_set, TxSet)
    assert isinstance(bl.header, Header)
    assert bl.hash == "dc963a34be8a8ae3065e07734a69c728f9e1c19cc08c54e189a1ed9097a465d2"
    assert bl.ecosystem_id == 0
    assert bl.node_position == 0
    assert bl.tx_count == 2
    assert bl.key_id == -5953874702473585171
    assert bl.time == 1535819403
    assert bl.rollbacks_hash == '95e1028b7fda373e07924ec015427d6c08ec74e62318c634fbf669b29cd68002'
    assert bl.mrkl_root == '7e66c0691376401a08dd6ae30c205e981ab596104bc7208e93962785daa9d487'
    assert bl.bin_data == None
    assert bl.sys_update == False
    assert bl.gen_block == False
    assert bl.stop_count == 0
    assert bl.header.block_id == '123'
    assert bl.header.time == 1535819403
    assert bl.header.ecosystem_id == 0
    assert bl.header.node_position == 0
    assert bl.header.sign == 'e8b56c269a60ea33c662fff0a5fbf3fbff7e09ce383ce5cc58015c38507ad01293d3ab60ed2d91e1611cc5c59099155eb326a74fccbfe57113b27cce8010cc20'
    assert bl.header.hash == "9103d67766acc5b0834ee059b4010348dad5e9e9816f820b2ecbee4ea455a2a7"
    assert bl.header.version == 1


@with_setup(my_setup, my_teardown)
def test_block_to_dict():
    b = d1[0]
    bl = Block(from_dict=b)

    d = bl.to_dict()
    assert type(d) == dict
    block_id = get_block_id_from_dict(b)
    assert block_id
    assert block_id in b
    transactions = get_block_data_from_dict(b)
    assert type(transactions) == list
    assert len(transactions) == len(bl.txs)
    i = 0
    while i < len(b[block_id]):
        assert transactions[i] == b[block_id][i]
        i += 1

    d = bl.to_dict(struct_style='sqlalchemy')
    assert type(d) == dict
    assert 'block_id' in d
    assert 'transactions' in d
    block_id = d['block_id']
    assert block_id
    transactions = d['transactions']
    assert type(transactions) == list
    assert len(transactions) == len(bl.txs)
    i = 0
    while i < len(b[block_id]):
        assert transactions[i] == b[block_id][i]
        i += 1

    update_data = {
        'addkey1': 'addval1',
        'addkey2': 'addval2',
    }
    d = bl.to_dict(struct_style='sqlalchemy', update_data=update_data)
    assert type(d) == dict
    assert 'block_id' in d
    assert 'transactions' in d
    for k, v in update_data.items():
        assert k in d
        assert d[k] == v


    b = d3[0]
    bl = Block(b64decode_hashes=True)
    bl.from_detailed_dict(b)
    d = bl.to_dict(struct_style='sqlalchemy')
    assert 'block_id' in d
    assert 'header' in d
    assert 'transactions' in d

    assert d['block_id'] == get_block_id_from_dict(b)
    assert d['hash'] == "dc963a34be8a8ae3065e07734a69c728f9e1c19cc08c54e189a1ed9097a465d2"
    assert d['ecosystem_id'] == 0
    assert d['node_position'] == 0
    assert d['tx_count'] == 2
    assert d['key_id'] == -5953874702473585171
    assert d['time'] == 1535819403
    assert d['rollbacks_hash'] == '95e1028b7fda373e07924ec015427d6c08ec74e62318c634fbf669b29cd68002'
    assert d['mrkl_root'] == '7e66c0691376401a08dd6ae30c205e981ab596104bc7208e93962785daa9d487'
    assert d['bin_data'] == None
    assert d['sys_update'] == False
    assert d['gen_block'] == False
    assert d['stop_count'] == 0
    assert d['header']['block_id'] == '123'
    assert d['header']['time'] == 1535819403
    assert d['header']['ecosystem_id'] == 0
    assert d['header']['node_position'] == 0
    assert d['header']['sign'] == 'e8b56c269a60ea33c662fff0a5fbf3fbff7e09ce383ce5cc58015c38507ad01293d3ab60ed2d91e1611cc5c59099155eb326a74fccbfe57113b27cce8010cc20'
    assert d['header']['hash'] == "9103d67766acc5b0834ee059b4010348dad5e9e9816f820b2ecbee4ea455a2a7"
    assert d['header']['version'] == 1
