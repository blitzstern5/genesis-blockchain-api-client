from nose import with_setup

from genesis_blockchain_api_client.blockchain.tx_set import TxSet
from genesis_blockchain_api_client.blockchain.tx import Tx

from .blockchain_commons import d1, get_txs

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_txs_object_creation():
    ts = get_txs(d1[0])
    cnt = 0
    txs = TxSet()
    for t in ts:
        tx = Tx(**t)
        txs.add(tx)
        assert txs.txs[cnt] == tx
        cnt += 1
    assert len(txs.txs) == len(ts)

@with_setup(my_setup, my_teardown)
def test_txs_from_list():
    ts = get_txs(d1[0])
    txs = TxSet(from_list=ts)
    assert len(txs.txs) == len(ts)

@with_setup(my_setup, my_teardown)
def test_tx_to_list():
    ts = get_txs(d1[0])
    txs = TxSet(from_list=ts)
    txsl = txs.to_list(style='camel')

    assert len(ts) == len(txsl)

    i = 0
    while i < len(ts):
        for n in ('Hash', 'ContractName', 'Params', 'KeyID'):
            assert txsl[i][n] == ts[i][n]
        i += 1

