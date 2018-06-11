from typing import Mapping
import decision_engine.meta_func
import abc


class VarGenRule(object):
    def __init__(self, name, rule):
        self.name = name
        self.rule = rule


class Val(object):
    def __init__(self, val, data_type):
        self.val = val  # type: any
        self.data_type = data_type  # type: type or decision_engine.meta_func.MetaFunc


class ArrList(list):
    @staticmethod
    @abc.abstractmethod
    def ele_type() -> type:
        pass

    def __init__(self, *args):
        if [x for x in args[0] if not isinstance(x, self.ele_type)].__len__() != 0:
            raise TypeError
        list.__init__([])
        self.extend(args[0])

    def __add__(self, other):
        if type(self) != type(other):
            raise TypeError
        return super(ArrList, self).__add__(other)

    def __setitem__(self, key, value):
        if not isinstance(value, self.ele_type):
            raise TypeError
        super(ArrList, self).__setitem__(key, value)


class ArrInt(ArrList):
    @staticmethod
    def ele_type():
        return int


class ArrFloat(ArrList):
    @staticmethod
    def ele_type():
        return float


class ArrStr(ArrList):
    @staticmethod
    def ele_type():
        return str


class ArrBool(ArrList):
    @staticmethod
    def ele_type():
        return bool


NameSpace = Mapping[str, Val]


