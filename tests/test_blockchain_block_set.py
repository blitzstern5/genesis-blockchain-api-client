from nose import with_setup

import base64

from genesis_blockchain_api_client.blockchain.tx_set import TxSet
from genesis_blockchain_api_client.blockchain.block import Block
from genesis_blockchain_api_client.blockchain.block.header import Header
from genesis_blockchain_api_client.blockchain.block_set import BlockSet
from .blockchain_commons import d1, d2, d3, d4, get_txs

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_blocks_from_list():
    bs = d1
    bls = BlockSet()
    bls.from_list(bs)
    assert len(bls.blocks) == len(bs)
    i = 0
    while i < len(bls.blocks):
        assert isinstance(bls.blocks[0], Block)
        assert isinstance(bls.blocks[0].tx_set, TxSet)
        ts = get_txs(d1[i])
        txs = TxSet(from_list=ts)
        j = 0
        while j < len(bls.blocks[i].tx_set.txs):
            for n in ('hash', 'contract_name', 'params', 'key_id'):
                assert getattr(bls.blocks[i].tx_set.txs[j], n) == getattr(txs.txs[j], n)
            j += 1
        i += 1

@with_setup(my_setup, my_teardown)
def test_blocks_from_dict():
    bs = d2
    bls = BlockSet()
    bls.from_dict(bs)
    assert len(bls.blocks) == len(bs)
    i = 0
    while i < len(bls.blocks):
        i += 1

    bls = BlockSet(from_dict=bs)
    assert len(bls.blocks) == len(bs)
    i = 0
    while i < len(bls.blocks):
        i += 1

def check_block_set_with_detailed_dict(bs, dd):
    """ bs - block set, dd - detailed dict """
    dd = dict(dd)
    assert len(bs.blocks) == len(dd)
    i = 0
    for block_id, block_data in dd.items():
        for b_key, b_val in block_data.items():
            if b_key == 'header':
                if hasattr(bs.blocks[i], b_key):
                    for h_key, h_val in b_val.items():
                        assert hasattr(bs.blocks[i].header, h_key)
                        if h_key in ('hash', 'sign',):
                            if h_val:
                                assert getattr(bs.blocks[i].header, h_key) == base64.b64decode(h_val).hex()
                            else:
                                assert getattr(bs.blocks[i].header, h_key) == None

                        else:
                            assert getattr(bs.blocks[i].header, h_key) == h_val
            elif b_key == 'transactions':
                if hasattr(bs.blocks[i], 'tx_set'):
                    j = 0
                    for tx_data in b_val:
                        t_key = tuple(tx_data.keys())[0]
                        t_val = tx_data[t_key]
                        assert hasattr(bs.blocks[i].tx_set.txs[j], t_key)
                        if t_key in ('hash',):
                            if t_val:
                                assert getattr(bs.blocks[i].tx_set.txs[j], t_key) == base64.b64decode(t_val).hex()
                            else:
                                assert not getattr(bs.blocks[i].tx_set.txs[j], t_key)
                        else:
                            assert getattr(bs.blocks[i].tx_set.txs[j], t_key) == t_val
                        j += 1
            else:
                assert hasattr(bs.blocks[i], b_key)
                if b_key in ('hash', 'rollbacks_hash'):
                    assert getattr(bs.blocks[i], b_key) == base64.b64decode(block_data[b_key]).hex()
                elif b_key in ('mrkl_root',):
                    assert getattr(bs.blocks[i], b_key) == base64.b64decode(block_data[b_key]).decode()
                elif b_key in ('time',):
                    assert getattr(bs.blocks[i], b_key) == block_data[b_key]
                else:
                    assert getattr(bs.blocks[i], b_key) == block_data[b_key]
        i += 1
        
def test_blocks_from_detailed_dict():
    bs = BlockSet(b64decode_hashes=True)
    bs.from_detailed_dict(dict(d4))
    assert d4 == dict(d4)
    check_block_set_with_detailed_dict(bs, d4)

@with_setup(my_setup, my_teardown)
def test_blocks_to_list():
    bs = d1
    bs = BlockSet()
    bs.from_list(d1)
    assert len(bs.blocks) == len(d1)
    bs = bs.to_list(style='camel')
    assert bs == d1

    bs = BlockSet(from_list=bs)
    assert len(bs.blocks) == len(d1)
    bs = bs.to_list(style='camel')
    assert bs == d1

def check_detailed_list(blsl):
    assert type(blsl) == list
    assert len(blsl) == len(d2)
    i = 0
    while i < len(blsl):
        assert 'block_id' in blsl[i]
        assert blsl[i]['block_id']
        if 'header' in blsl[i]:
            assert type(blsl[i]['header']) == dict 
        if 'transactions' in blsl[i]:
            assert type(blsl[i]['transactions']) ==list
        i += 1

@with_setup(my_setup, my_teardown)
def test_blocks_to_detailed_list():
    bs = BlockSet(from_list=d1)
    assert len(bs.blocks) == len(d1)
    bs = bs.to_detailed_list(style='camel')
    check_detailed_list(bs)

    bs = BlockSet(b64decode_hashes=True, from_detailed_dict=d4)
    check_block_set_with_detailed_dict(bs, d4)

