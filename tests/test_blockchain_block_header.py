from nose import with_setup

from genesis_blockchain_api_client.blockchain.block.header import Header
from genesis_blockchain_api_client.blockchain.block import (
    get_block_id_from_dict,
    get_block_data_from_dict,
)
from .blockchain_commons import d3, get_txs

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_block_header_from_dict():
    b = get_block_data_from_dict(d3[0])
    bh = Header(b64decode_hashes=True)
    bh.from_dict(b['header'])

    assert bh.block_id == '123'
    assert bh.time == 1535819403
    assert bh.ecosystem_id == 0
    assert bh.node_position == 0
    assert bh.sign == 'e8b56c269a60ea33c662fff0a5fbf3fbff7e09ce383ce5cc58015c38507ad01293d3ab60ed2d91e1611cc5c59099155eb326a74fccbfe57113b27cce8010cc20'
    assert bh.hash == "9103d67766acc5b0834ee059b4010348dad5e9e9816f820b2ecbee4ea455a2a7"
    assert bh.version == 1

    bh = Header(b64decode_hashes=False)
    bh.from_dict(b['header'])

    assert bh.block_id == '123'
    assert bh.time == 1535819403
    assert bh.ecosystem_id == 0
    assert bh.node_position == 0
    assert bh.sign == '6LVsJppg6jPGYv/wpfvz+/9+Cc44POXMWAFcOFB60BKT06tg7S2R4WEcxcWQmRVesyanT8y/5XETsnzOgBDMIA=='
    assert bh.hash == "kQPWd2asxbCDTuBZtAEDSNrV6emBb4ILLsvuTqRVoqc="
    assert bh.version == 1
