import base64
import logging
import binascii

from ..tx_set import TxSet
from ...utils import camel_to_snake

logger = logging.getLogger(__name__)

class Header:
    def add(self, name, val):
        if not self._ignore_undeclared_fields or name in self._fields:
            self._fields_num += 1
            setattr(self, name, val)
        else:
            logger.warning("field '%s' is wasn't declared and skipped")

    def from_dict(self, d):
        for field in self._fields:
            if field in d:
                val = d[field]
                if val and self._b64decode_hashes and field in self._b64fields:
                    try:
                        val = base64.b64decode(val).hex()
                    except binascii.Error:
                        logger.warning("cannot b64code %s: %s" % (field, val))
                self.add(field, val)

    def set_defaults(self):
        for field in self._fields:
            setattr(self, field, None)

    def __init__(self, **kwargs):
        self._ignore_undeclared_fields = bool(kwargs.pop('ignore_undeclared_fields', True))
        self._fields_num = 0
        self._fields = ('block_id', 'time', 'ecosystem_id', 'key_id',
                        'node_position', 'sign', 'hash', 'version')
        self.set_defaults()
        self._b64fields = ('hash', 'sign')
        self._b64decode_hashes = kwargs.pop('b64decode_hashes', False)
        logger.debug("self._b64decode_hashes: %s" % self._b64decode_hashes)
        d = kwargs.get('from_dict')
        if d:
            self.from_dict(d)
        else:
            self.from_dict(kwargs)

    @property
    def count(self):
        return self._fields_num

    def to_dict(self, style='camel', struct_style='backend', update_data={}):
        d = {}
        for field in self._fields:
            val = getattr(self, field)
            if style == 'snake':
                field = camel_to_snake(field)
            d[field] = val
        return d
    
    def __str__(self):
        return str(self.to_dict(style='snake'))

    def __repr__(self):
        return str(self)

