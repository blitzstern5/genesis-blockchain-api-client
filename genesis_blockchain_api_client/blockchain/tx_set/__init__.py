import logging

from ..tx import Tx

logger = logging.getLogger(__name__)

class TxSet:

    def add(self, tx):
        self._tx_num += 1
        self.txs.append(tx)

    def from_list(self, l):
        for item in l:
            if self.b64decode_hashes:
                item['b64decode_hashes'] = self.b64decode_hashes
            tx = Tx(**item)
            self.add(tx)

    def __init__(self, **kwargs):
        self._tx_num = 0
        self.b64decode_hashes = kwargs.pop('b64decode_hashes', False)
        logger.debug("self.b64decode_hashes: %s" % self.b64decode_hashes)
        self.txs = kwargs.get('txs', []) 
        l = kwargs.get('from_list')
        if l:
            self.from_list(l)

    @property
    def size(self):
        return self._tx_num

    def to_list(self, style='camel'):
        l = []
        for tx in self.txs:
            l.append(tx.to_dict(style=style))
        return l

    def __str__(self):
        return str(self.to_list(style='snake'))

    def __repr__(self):
        return str(self)


