import base64
import logging

from ..tx_set import TxSet
from .header import Header

logger = logging.getLogger(__name__)

def get_block_id_from_dict(d):
    return tuple(d.keys())[0]

def get_block_data_from_dict(d):
    return d[get_block_id_from_dict(d)]

class Block:
    def from_dict(self, d):
        self.id = get_block_id_from_dict(d)
        self.tx_set = TxSet(from_list=get_block_data_from_dict(d),
                            b64decode_hashes=self._b64decode_hashes)

    def from_detailed_dict(self, d):
        self.id = get_block_id_from_dict(d)
        data = get_block_data_from_dict(d)
        for field in self._fields:
            if field in data:
                val = data[field]
                if self._b64decode_hashes:
                    if field in self._b64fields:
                        val = base64.b64decode(val).hex()
                    elif field == 'mrkl_root':
                        val = base64.b64decode(val).decode()
                setattr(self, field, val)
        if not 'header' in data:
            header = {}
        else:
            header = data['header']
        self.header = Header(from_dict=header, b64decode_hashes=self._b64decode_hashes)
        if not 'transactions' in data:
            txs = []
        else:
            txs = data['transactions']
        self.tx_set = TxSet() #from_list=txs, b64decode_hashes=self._b64decode_hashes)

    def __init__(self, **kwargs):
        self.header = Header()
        self.tx_set = TxSet()
        self._b64decode_hashes = kwargs.pop('b64decode_hashes', False)
        self._fields = ('hash', 'ecosystem_id', 'node_position', 'key_id', 'time',
                        'tx_count', 'rollbacks_hash', 'mrkl_root', 'bin_data',
                        'sys_update', 'gen_block', 'stop_count')
        self._b64fields = ('hash', 'rollbacks_hash')
        logger.debug("self._b64decode_hashes: %s" % self._b64decode_hashes)
        self.id = kwargs.get('id') 
        self.tx_set = kwargs.get('tx_set')
        d = kwargs.get('from_dict')
        if d:
            self.from_dict(d)
        d = kwargs.get('from_detailed_dict')
        if d:
            self.from_detailed_dict(d)

    def to_dict(self, style='camel', struct_style='backend', update_data={}):
        if struct_style == 'backend':
            return {self.id: self.tx_set.to_list(style=style)}
        else:
            d = {'block_id': self.id}
            for field in self._fields:
                if hasattr(self, field):
                    d[field] = getattr(self, field)
            if self.header.size:
                d['header'] = self.header.to_dict(style=style, struct_style=struct_style)
            d['transactions'] = self.tx_set.to_list(style=style)
            if update_data:
                d.update(update_data)
            return d
    
    def __str__(self):
        return str(self.to_dict(style='snake'))

    def __repr__(self):
        return str(self)

    @property
    def txs(self):
        return self.tx_set.txs
