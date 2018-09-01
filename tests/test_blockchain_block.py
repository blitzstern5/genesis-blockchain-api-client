from nose import with_setup

from genesis_blockchain_api_client.blockchain.tx_set import TxSet
from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)

from .blockchain_commons import d1, get_txs

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
