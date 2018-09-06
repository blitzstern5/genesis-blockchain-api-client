from nose import with_setup

from genesis_blockchain_api_client.blockchain.tx_set import TxSet
from genesis_blockchain_api_client.blockchain.block import Block
from genesis_blockchain_api_client.blockchain.block.header import Header
from genesis_blockchain_api_client.blockchain.block_set import BlockSet
from .blockchain_commons import d1, d2, d4, get_txs

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

def test_blocks_from_detailed_dict():
    bs = d4
    bls = BlockSet(b64decode_hashes=True)
    bls.from_detailed_dict(bs)
    assert len(bls.blocks) == len(bs)

    assert bls.blocks[0].id == '123'
    assert isinstance(bls.blocks[0].tx_set, TxSet)
    assert isinstance(bls.blocks[0].header, Header)
    print("bls.blocks[0].hash: %s" % bls.blocks[0].hash)
    #assert bls.blocks[0].hash == "dc963a34be8a8ae3065e07734a69c728f9e1c19cc08c54e189a1ed9097a465d2"
    #assert bls.blocks[0].ecosystem_id == 0
    #assert bls.blocks[0].node_position == 0
    #assert bls.blocks[0].tx_count == 2
    #assert bls.blocks[0].key_id == -5953874702473585171
    #assert bls.blocks[0].time == 1535819403
    #assert bls.blocks[0].rollbacks_hash == '95e1028b7fda373e07924ec015427d6c08ec74e62318c634fbf669b29cd68002'
    #assert bls.blocks[0].mrkl_root == '7e66c0691376401a08dd6ae30c205e981ab596104bc7208e93962785daa9d487'
    #assert bls.blocks[0].bin_data == None
    #assert bls.blocks[0].sys_update == False
    #assert bls.blocks[0].gen_block == False
    #assert bls.blocks[0].stop_count == 0
    #assert bls.blocks[0].header.block_id == '123'
    #assert bls.blocks[0].header.time == 1535819403
    #assert bls.blocks[0].header.ecosystem_id == 0
    #assert bls.blocks[0].header.node_position == 0
    #assert bls.blocks[0].header.sign == 'e8b56c269a60ea33c662fff0a5fbf3fbff7e09ce383ce5cc58015c38507ad01293d3ab60ed2d91e1611cc5c59099155eb326a74fccbfe57113b27cce8010cc20'
    #assert bls.blocks[0].header.hash == "9103d67766acc5b0834ee059b4010348dad5e9e9816f820b2ecbee4ea455a2a7"
    #assert bls.blocks[0].header.version == 1

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

@with_setup(my_setup, my_teardown)
def test_blocks_to_detailed_list():
    bs = d1
    bls = BlockSet(from_list=bs)
    assert len(bls.blocks) == len(bs)
    blsl = bls.to_detailed_list(style='camel')
    assert type(blsl) == list
    assert len(blsl) == len(d2)
    i = 0
    while i < len(blsl):
        assert 'block_id' in blsl[i]
        assert blsl[i]['block_id']
        if 'transactions' in blsl[i]:
            assert type(blsl[i]['transactions']) ==list
        i += 1

