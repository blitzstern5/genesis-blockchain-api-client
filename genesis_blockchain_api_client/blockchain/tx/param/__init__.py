from ....utils import camel_to_snake

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

    def __str__(self):
        return str({self.oname: self.value})

    def __repr__(self):
        return {self.oname: self.value}
