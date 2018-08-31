from nose import with_setup

from genesis_blockchain_api_client.blockchain.tx.param import (
    Param, get_first_kv
)
from genesis_blockchain_api_client.blockchain.tx.param_set import ParamSet
from genesis_blockchain_api_client.utils import camel_to_snake

from .blockchain_commons import d1, get_txs

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_param_set_object_creation():
    _ps = get_txs(d1[0])[0]['Params']
    ps = ParamSet(**_ps)
    assert ps.get_names() == ['param_name1', 'param_name2']
    assert ps.get_orig_names() == ['ParamName1', 'ParamName2']
    assert getattr(ps, 'param_name1') == 'val1'
    assert getattr(ps, 'param_name2') == 'val2'
    assert str(ps) == "| ParamSet: {'param_name1': 'val1', 'param_name2': 'val2'} |"



