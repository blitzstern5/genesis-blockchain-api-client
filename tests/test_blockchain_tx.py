from nose import with_setup

from genesis_blockchain_api_client.blockchain.tx.param_set import ParamSet
from genesis_blockchain_api_client.blockchain.tx import Tx

from .blockchain_commons import d1, get_txs

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_tx_object_creation():
    t = get_txs(d1[0])[0]
    tx = Tx(hash=t['Hash'], contract_name=t['ContractName'], params=t['Params'],
            key_id=t['KeyID'])
    assert tx.hash == t['Hash']
    assert tx.contract_name == t['ContractName']
    assert tx.params == t['Params']
    assert tx.key_id == t['KeyID']

@with_setup(my_setup, my_teardown)
def test_tx_from_dict():
    t = get_txs(d1[0])[0]

    tx = Tx()
    tx.from_dict(t)
    assert tx.hash == t['Hash']
    assert tx.contract_name == t['ContractName']
    assert tx.params == t['Params']
    assert tx.key_id == t['KeyID']

    tx = Tx(from_dict=t)
    assert tx.hash == t['Hash']
    assert tx.contract_name == t['ContractName']
    assert tx.params == t['Params']
    assert tx.key_id == t['KeyID']

    tx = Tx(**t)
    assert tx.hash == t['Hash']
    assert tx.contract_name == t['ContractName']
    assert tx.params == t['Params']
    assert tx.key_id == t['KeyID']

    t_ = {'hash': t['Hash'], 'contract_name': t['ContractName'],
          'params': t['Params'], 'key_id': t['KeyID']}
    tx = Tx(from_dict=t_)
    assert tx.hash == t['Hash']
    assert tx.contract_name == t['ContractName']
    assert tx.params == t['Params']
    assert tx.key_id == t['KeyID']

@with_setup(my_setup, my_teardown)
def test_tx_to_dict():
    t = get_txs(d1[0])[0]
    tx = Tx(**t)
    txd = tx.to_dict(style='camel')
    for n in ('Hash', 'ContractName', 'Params', 'KeyID'):
        assert txd[n] == t[n]
