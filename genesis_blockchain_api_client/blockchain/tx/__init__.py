import base64
import logging
import binascii

from .param_set import ParamSet

logger = logging.getLogger(__name__)

class Tx:
    def from_dict(self, d):
        self.hash = d.get('Hash', d.get('hash'))
        logger.debug("b64decode_hashes: %s" % self.b64decode_hashes)
        if self.hash and self.b64decode_hashes:
            try:
                self.hash = base64.b64decode(self.hash).hex()
            except binascii.Error:
                logger.warning("cannot b64 decode hash: %s" % self.hash)
        self.contract_name = d.get('ContractName', d.get('contract_name'))
        self.params = d.get('Params', d.get('params'))
        self.param_set = None
        if self.params:
            self.param_set = ParamSet(**self.params)
        self.key_id = d.get('KeyID', d.get('key_id')) 
        self.time = d.get('Time', d.get('time')) 
        self.type = d.get('Type', d.get('type')) 

    def __init__(self, **kwargs):
        self.b64decode_hashes = kwargs.pop('b64decode_hashes', False)
        logger.debug("self.b64decode_hashes: %s" % self.b64decode_hashes)
        self.from_dict(kwargs)
        d = kwargs.get('from_dict')
        if d:
            self.from_dict(d)

    def to_dict(self, style='camel'):
        d = {}
        if style == 'camel':
            names_map = {'Hash': 'hash', 'ContractName': 'contract_name',
                         'Params': 'params', 'KeyID': 'key_id', 'Time': 'time', 'type': 'Type'}
        else:
            names_map = {'hash': 'hash', 'contract_name': 'contract_name',
                         'params': 'params', 'key_id': 'key_id', 'time': 'time', 'type': 'type'}
        for name_to, name_from in names_map.items():
            try:
                if not getattr(self, name_from) is None:
                    d[name_to] = getattr(self, name_from)
            except AttributeError:
                pass
        return d

    def __str__(self):
        return str(self.to_dict(style='snake'))

    def __repr__(self):
        return str(self)
