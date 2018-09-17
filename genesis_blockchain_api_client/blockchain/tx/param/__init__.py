from ....utils import camel_to_snake
    #bs.from_detailed_dict(d4)

def get_first_kv(d):
    n = tuple(d.keys())[0]
    return n, d[n]

class Param:
    def __init__(self, *args, **kwargs):
        if args:
            self.oname, self.value = args[0], args[1] if len(args) > 1 else None
        if kwargs:
            self.oname, self.value = get_first_kv(kwargs)
        self.name = camel_to_snake(self.oname)

    def to_dict(self, style='camel', struct_style='sqlalchemy'):
        if style == 'camel':
            if struct_style == 'simple_dict':
                return {self.oname: self.value}
            else:
                return {'name': self.oname, 'value': self.value}
        else:
            if struct_style == 'simple_dict':
                return {self.name: self.value}
            else:
                return {'name': self.name, 'value': self.value}

    def __str__(self):
        return str({self.oname: self.value})

    def __repr__(self):
        return {self.oname: self.value}
