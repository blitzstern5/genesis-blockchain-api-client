from ..tx_set import TxSet

def get_block_id_from_dict(d):
    return tuple(d.keys())[0]

def get_block_data_from_dict(d):
    return d[get_block_id_from_dict(d)]

class Block:
    def from_dict(self, d):
        self.id = get_block_id_from_dict(d)
        self.tx_set = TxSet(from_list=get_block_data_from_dict(d))

    def __init__(self, **kwargs):
        self.id = kwargs.get('id') 
        self.tx_set = kwargs.get('tx_set')
        d = kwargs.get('from_dict')
        if d:
            self.from_dict(d)

    def to_dict(self, style='camel', struct_style='backend', update_data={}):
        if struct_style == 'backend':
            d = {self.id: self.tx_set.to_list(style=style)}
        else:
            d = {
                    'block_id': self.id,
                    'transactions': self.tx_set.to_list(style=style),
                }
        if update_data:
            d.update(update_data)
        return d
    
    def __str__(self):
        return '| Block: ' + str(self.to_dict(style='snake')) + ' |'

    def __repr__(self):
        return str(self)

    @property
    def txs(self):
        return self.tx_set.txs
