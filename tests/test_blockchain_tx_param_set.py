from nose import with_setup

from genesis_blockchain_api_client.blockchain.tx.param import (
    Param, get_first_kv
)
from genesis_blockchain_api_client.blockchain.tx.param import Param
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
    assert str(ps) == "{'param_name1': 'val1', 'param_name2': 'val2'}"

@with_setup(my_setup, my_teardown)
def test_param_set_iter():
    _ps = get_txs(d1[0])[0]['Params']
    ps = ParamSet(**_ps)
    for name, value in ps.items():
        pass
    for name, value in _ps.items():
        assert value == ps[camel_to_snake(name)]

@with_setup(my_setup, my_teardown)
def test_param_set_to_dict():
    p = get_txs(d1[0])[0]['Params']
    ps = ParamSet(**p)
    d = ps.to_dict()
    for name, value in p.items():
        assert name in d
        assert value == d[name]

@with_setup(my_setup, my_teardown)
def test_param_set_to_list():
    p = get_txs(d1[0])[0]['Params']
    ps = ParamSet(**p)
    l = ps.to_list()

    i = 0
    for name, value in p.items():
        assert name in l[i]
        assert l[i][name] == value
        i += 1

    ps = ParamSet(**p)
    l = ps.to_list(style='snake')
    i = 0
    for name, value in p.items():
        assert camel_to_snake(name) in l[i]
        assert l[i][camel_to_snake(name)] == value
        i += 1
