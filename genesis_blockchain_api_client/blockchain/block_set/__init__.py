import logging

from ..block import Block, get_block_id_from_dict, get_block_data_from_dict

logger = logging.getLogger(__name__)

class BlockSet:
    def add(self, block):
        self.blocks.append(block)

    def from_list(self, l):
        for item in l:
            block = Block(from_dict=item, b64decode_hashes=self._b64decode_hashes)
            self.add(block)

    def from_dict(self, d):
        for block_id, data in d.items():
            block = Block(from_dict={block_id: data},
                          b64decode_hashes=self._b64decode_hashes)
            self.add(block)

    def from_detailed_dict(self, d):
        for block_id, data in d.items():
            block = Block(from_detailed_dict={block_id: data},
                          b64decode_hashes=self._b64decode_hashes)
            self.add(block)

    def __init__(self, **kwargs):
        self._b64decode_hashes = kwargs.get('b64decode_hashes', False)
        logger.debug("self._b64decode_hashes: %s" % self._b64decode_hashes)
        self.blocks = kwargs.get('blocks', []) 
        l = kwargs.get('from_list')
        if l:
            self.from_list(l)
        d = kwargs.get('from_dict')
        if d:
            self.from_dict(d)
        d = kwargs.get('from_detailed_dict')
        if d:
            self.from_detailed_dict(d)

    @property
    def count(self):
        return len(self.blocks)

    def to_list(self, style='camel'):
        l = []
        for block in self.blocks:
            l.append(block.to_dict(style=style))
        return l

    def to_detailed_list(self, style='camel'):
        l = []
        for block in self.blocks:
            l.append(block.to_dict(style=style, struct_style='sqlalchemy'))
        return l

    def __str__(self):
        return str(self.to_list(style='snake'))

    def __repr__(self):
        return str(self)

