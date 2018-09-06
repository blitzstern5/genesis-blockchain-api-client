import logging

from ..tx import Tx

logger = logging.getLogger(__name__)

class TxSet:

    def add(self, tx):
        self.txs.append(tx)

    def from_list(self, l):
        for item in l:
            tx = Tx(from_dict=item, b64decode_hashes=self.b64decode_hashes)
            self.add(tx)

    def __init__(self, **kwargs):
        self.b64decode_hashes = kwargs.pop('b64decode_hashes', False)
        logger.debug("self.b64decode_hashes: %s" % self.b64decode_hashes)
        self.txs = kwargs.get('txs', []) 
        l = kwargs.get('from_list')
        if l:
            self.from_list(l)

    @property
    def count(self):
        return len(self.txs)

    def to_list(self, style='camel'):
        l = []
        for tx in self.txs:
            l.append(tx.to_dict(style=style))
        return l

    def __str__(self):
        return str(self.to_list(style='snake'))

    def __repr__(self):
        return str(self)


