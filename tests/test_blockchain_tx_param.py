from nose import with_setup

from genesis_blockchain_api_client.blockchain.tx.param import (
    Param, get_first_kv
)
from genesis_blockchain_api_client.utils import camel_to_snake

from .blockchain_commons import d1, get_txs

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_get_first_kv():
    ps = get_txs(d1[0])[0]['Params']
    kv = get_first_kv(ps)
    assert kv == ('ParamName1', 'val1')

@with_setup(my_setup, my_teardown)
def test_param_object_creation():
    ps = get_txs(d1[0])[0]['Params']

    kv = get_first_kv(ps)
    tp = Param(*kv)
    assert tp.oname == kv[0]
    assert tp.name == camel_to_snake(kv[0])
    assert tp.value == kv[1]

    kv = get_first_kv(ps)
    kvd = {kv[0]: kv[1]}
    tp = Param(**kvd)
    assert tp.oname == kv[0]
    assert tp.name == camel_to_snake(kv[0])
    assert tp.value == kv[1]

@with_setup(my_setup, my_teardown)
def test_param_to_dict():
    ps = get_txs(d1[0])[0]['Params']
    kv = get_first_kv(ps)
    p = Param(*kv)
    pd = p.to_dict()
    assert pd['name'] == kv[0]
    assert pd['value'] == kv[1]
    pd = p.to_dict(style='backend')
    assert pd['name'] == camel_to_snake(kv[0])
    assert pd['value'] == kv[1]
