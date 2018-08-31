from ..block import Block

class BlockSet:
    def add(self, block):
        self.blocks.append(block)

    def from_list(self, l):
        for item in l:
            block = Block(from_dict=item)
            self.add(block)

    def from_dict(self, d):
        for block_id, data in d.items():
            block_d = {block_id: data}
            block = Block(from_dict={block_id: data})
            self.add(block)

    def __init__(self, **kwargs):
        self.blocks = kwargs.get('blocks', []) 
        l = kwargs.get('from_list')
        if l:
            self.from_list(l)
        d = kwargs.get('from_dict')
        if d:
            self.from_dict(d)

    def to_list(self, style='camel'):
        l = []
        for block in self.blocks:
            l.append(block.to_dict(style=style))
        return l

    def __str__(self):
        return '| BlockSet: ' + str(self.to_list(style='snake')) + ' |'

    def __repr__(self):
        return str(self)

