from collections import Mapping

from ....utils import camel_to_snake

from ..param import Param

class ParamSet(Mapping):

    def add(self, param):
        self.__orig_names.append(param.oname)
        self.__names.append(param.name)
        self.__items.append(param)
        setattr(self, param.name, param.value)

    def get_names(self):
        return self.__names

    def get_orig_names(self):
        return self.__orig_names

    def get_orig_items(self):
        return self.__orig_items

    def from_dict(self, d):
        self.__orig_items = d
        for k, v in d.items():
            d = {k: v}
            p = Param(**d)
            self.add(p)

    def __init__(self, **kwargs):
        self.__orig_names = []
        self.__names = []
        self.__items = []
        self.from_dict(kwargs)

    def __iter__(self):
        for item in self.__items:
            yield item.name

    def __getitem__(self, name):
        try:
            return self.__items[self.__names.index(name)].value
        except ValueError:
            raise KeyError

    def __len__(self):
        return len(self.__items)

    def count(self):
        return len(self.__items)

    def to_dict(self, style='camel'):
        d = {}
        for item in self.__items:
            if style == 'camel':
                d[item.oname] = item.value
            else:
                d[item.name] = item.value
        return d

    def to_list(self, style='camel'):
        l = []
        for item in self.__items:
            d = {}
            if style == 'camel':
                d[item.oname] = item.value
            else:
                d[item.name] = item.value
            l.append(d)
        return l

    def __str__(self):
        return str(self.to_dict(style='snake'))

    def __repr__(self):
        return str(self)

