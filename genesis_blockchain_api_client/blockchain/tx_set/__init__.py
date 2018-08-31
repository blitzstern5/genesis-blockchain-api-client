from ..tx import Tx

class TxSet:

    def add(self, tx):
        self.txs.append(tx)

    def from_list(self, l):
        for item in l:
            tx = Tx(**item)
            self.add(tx)

    def __init__(self, **kwargs):
        self.txs = kwargs.get('txs', []) 
        l = kwargs.get('from_list')
        if l:
            self.from_list(l)

    def to_list(self, style='camel'):
        l = []
        for tx in self.txs:
            l.append(tx.to_dict(style=style))
        return l

    def __str__(self):
        return '| TxSet: ' + str(self.to_list(style='snake')) + ' |'

    def __repr__(self):
        return str(self)


