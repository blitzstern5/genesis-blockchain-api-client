import base64

from .param_set import ParamSet

class Tx:
    def from_dict(self, d):
        self.hash = d.get('Hash', d.get('hash'))
        if self.b64decode_hashes:
            self.hash = base64.b64decode(self.hash)
        self.contract_name = d.get('ContractName', d.get('contract_name'))
        self.params = d.get('Params', d.get('params'))
        self.param_set = None
        if self.params:
            self.param_set = ParamSet(**self.params)
        self.key_id = d.get('KeyID', d.get('key_id')) 

    def __init__(self, **kwargs):
        self.b64decode_hashes = kwargs.pop('b64decode_hashes', False)
        self.from_dict(kwargs)
        d = kwargs.get('from_dict')
        if d:
            self.from_dict(d)

    def to_dict(self, style='camel'):
        d = {}
        if style == 'camel':
            names_map = {'Hash': 'hash', 'ContractName': 'contract_name',
                         'Params': 'params', 'KeyID': 'key_id'}
        else:
            names_map = {'hash': 'hash', 'contract_name': 'contract_name',
                         'params': 'params', 'key_id': 'key_id'}
        for name_to, name_from in names_map.items():
            try:
                d[name_to] = getattr(self, name_from)
            except AttributeError:
                pass
        return d

    def __str__(self):
        return '| Tx: ' + str(self.to_dict(style='snake')) + ' |'

    def __repr__(self):
        return str(self)
