from nose import with_setup

from genesis_blockchain_api_client.blockchain.tx_set import TxSet
from genesis_blockchain_api_client.blockchain.block import Block
from genesis_blockchain_api_client.blockchain.block_set import BlockSet
from .blockchain_commons import d1, d2, get_txs

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

@with_setup(my_setup, my_teardown)
def test_blocks_to_list():
    bs = d1
    bls = BlockSet()
    bls.from_list(bs)
    assert len(bls.blocks) == len(bs)
    blsl = bls.to_list(style='camel')
    assert blsl == bs

    bls = BlockSet(from_list=bs)
    assert len(bls.blocks) == len(bs)
    blsl = bls.to_list(style='camel')
    assert blsl == bs
