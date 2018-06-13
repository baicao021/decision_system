import decision_engine.basic_data_class as basic_data_class
from typing import Callable, Any, List, overload, Mapping, Union, Dict
from abc import ABCMeta, abstractmethod

NameSpace = Dict[str, basic_data_class.Val]
AtomFunc = Callable[[NameSpace], Any]


@overload
def auto_parser(val: int) -> 'IntFunc':
    pass


@overload
def auto_parser(val: float) -> 'FloatFunc':
    pass


@overload
def auto_parser(val: str) -> 'StrFunc':
    pass


@overload
def auto_parser(val: bool) -> 'BoolFunc':
    pass


def auto_parser(val: Union[int, float, str, bool]):
    p = {
        int: IntFunc,
        float: FloatFunc,
        str: StrFunc,
        bool: BoolFunc
    }.get(type(val))
    if p is not None:
        return p(val=val)
    raise TypeError


def auto_parser_dec(func):
    def operation(*args):
        args = [obj if isinstance(obj, MetaFunc) else auto_parser(obj) for obj in args]
        return func(*args)
    return operation


class MetaFunc(metaclass=ABCMeta):
    def __init__(self, name: str = None, val: Any = None, func: AtomFunc= None,
                 input_vars: Mapping[str, type] = None) -> None:
        self._input_vars = {}  # type: Mapping[str, type]

        if name is not None:
            self._input_vars = {
                name: self.data_type
            }
            self._func = lambda ns: ns[name]
        elif val is not None:
            self._func = lambda ns: val
        elif func is not None:
            self._func = func  # type: AtomFunc
            self._input_vars = input_vars
        else:
            raise TypeError

    def __call__(self, namespace: NameSpace):
        return self.func(namespace)

    @property
    def input_vars(self) -> Mapping[str, type]:
        return self._input_vars

    @property
    def func(self) -> AtomFunc:
        return self._func

    @property
    @abstractmethod
    def data_type(self) -> type:
        pass

    def union_input_vars(*other: 'MetaFunc'):
        ns_r = {}
        for meta_func in other:
            for k, v in meta_func.input_vars.items():
                if k in ns_r:
                    assert ns_r[k] == v
                else:
                    ns_r[k] = v
        return ns_r

    @abstractmethod
    def __lt__(self, other) -> 'BoolFunc':
        pass

    @abstractmethod
    def __eq__(self, other) -> 'BoolFunc':
        pass

    def __le__(self, other):
        return self.__lt__(other).or_(self.__eq__(other))

    def __ne__(self, other):
        return self.__eq__(other).not_()

    def __gt__(self, other):
        return self.__le__(other).not_()

    def __ge__(self, other):
        return self.__lt__(other).not_()


class IntFunc(MetaFunc):
    @property
    def func(self) -> Callable[[NameSpace], int]:
        return self._func

    @property
    def data_type(self):
        return int

    def __neg__(self):
        return IntFunc(
            input_vars=self.input_vars,
            func=lambda ns: -self.func(ns)
        )

    def to_float(self):
        return FloatFunc(
            input_vars=self.input_vars,
            func=lambda ns: float(self.func(ns))
        )

    def to_str(self):
        return StrFunc(
            input_vars=self.input_vars,
            func=lambda ns: str(self.func(ns))
        )

    @overload
    def __add__(self, other: 'IntFunc') -> 'IntFunc':
        pass

    @overload
    def __add__(self, other: 'FloatFunc') -> 'FloatFunc':
        pass

    @auto_parser_dec
    def __add__(self, other):
        f = {
            IntFunc: IntFunc,
            FloatFunc: FloatFunc
        }.get(type(other))
        if f is not None:
            return f(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) + other.func(ns)
            )
        raise TypeError

    def __radd__(self, other):
        return self.__add__(other)

    @auto_parser_dec
    def __sub__(self, other):
        return self.__add__(other.__neg__())

    @auto_parser_dec
    def __rsub__(self, other):
        return other + self.__neg__()

    @auto_parser_dec
    def __mul__(self, other):
        f = {
            IntFunc: IntFunc,
            FloatFunc: FloatFunc
        }.get(type(other))
        if f is not None:
            return f(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) * other.func(ns)
            )
        raise TypeError

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self.to_float() / other

    def __rtruediv__(self, other):
        return other / self.to_float()

    @auto_parser_dec
    def __lt__(self, other):
        if isinstance(other, IntFunc) or isinstance(other, FloatFunc):
            return BoolFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) < other.func(ns)
            )
        raise TypeError

    @auto_parser_dec
    def __eq__(self, other):
        if isinstance(other, IntFunc) or isinstance(other, FloatFunc):
            return BoolFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) == other.func(ns)
            )
        raise TypeError


class FloatFunc(MetaFunc):
    @property
    def func(self) -> Callable[[NameSpace], float]:
        return self._func

    @property
    def data_type(self):
        return float

    def to_str(self):
        return StrFunc(
            input_vars=self.input_vars,
            func=lambda ns: str(self.func(ns))
        )

    def __neg__(self):
        return FloatFunc(
            input_vars=self.input_vars,
            func=lambda ns: -self.func(ns)
        )

    def to_int(self):
        return IntFunc(
            input_vars=self.input_vars,
            func=lambda ns: int(self.func(ns))
        )

    @auto_parser_dec
    def __add__(self, other):
        if isinstance(other, FloatFunc) or isinstance(other, IntFunc):
            return FloatFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) + other.func(ns)
            )
        raise TypeError("%s, %s" % (type(self), type(other)))

    def __radd__(self, other):
        return self.__add__(other)

    @auto_parser_dec
    def __sub__(self, other):
        if isinstance(other, FloatFunc) or isinstance(other, IntFunc):
            return FloatFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) - other.func(ns)
            )
        raise TypeError

    def __rsub__(self, other):
        return self.__sub__(other).__neg__()

    @auto_parser_dec
    def __mul__(self, other):
        if isinstance(other, FloatFunc) or isinstance(other, IntFunc):
            return FloatFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) * other.func(ns)
            )
        raise TypeError

    def __rmul__(self, other):
        return self.__mul__(other)

    @auto_parser_dec
    def __truediv__(self, other):
        if isinstance(other, FloatFunc) or isinstance(other, IntFunc):
            return FloatFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) / other.func(ns)
            )
        raise TypeError

    @auto_parser_dec
    def __rtruediv__(self, other):
        if isinstance(other, FloatFunc) or isinstance(other, IntFunc):
            return FloatFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: other.func(ns) / self.func(ns)
            )
        raise TypeError

    @auto_parser_dec
    def __lt__(self, other):
        if isinstance(other, FloatFunc) or isinstance(other, IntFunc):
            return BoolFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) < other.func(ns)
            )
        raise TypeError

    @auto_parser_dec
    def __eq__(self, other):
        if isinstance(other, FloatFunc) or isinstance(other, IntFunc):
            return BoolFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) == other.func(ns)
            )
        raise TypeError


class StrFunc(MetaFunc):
    @property
    def func(self) -> Callable[[NameSpace], str]:
        return self._func

    @property
    def data_type(self):
        return str

    @auto_parser_dec
    def __add__(self, other):
        if isinstance(other, StrFunc):
            return StrFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) + other.func(ns)
            )
        raise TypeError

    @auto_parser_dec
    def __lt__(self, other):
        if isinstance(other, StrFunc):
            return BoolFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) < other.func(ns)
            )
        raise TypeError

    @auto_parser_dec
    def __eq__(self, other):
        if isinstance(other, StrFunc):
            return BoolFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) == other.func(ns)
            )
        raise TypeError


class BoolFunc(MetaFunc):
    @property
    def func(self) -> Callable[[NameSpace], bool]:
        return self._func

    @property
    def data_type(self):
        return bool

    @auto_parser_dec
    def __lt__(self, other):
        if isinstance(other, BoolFunc):
            return BoolFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) < other.func(ns)
            )
        raise TypeError

    @auto_parser_dec
    def __eq__(self, other):
        if isinstance(other, BoolFunc):
            return BoolFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) == other.func(ns)
            )
        raise TypeError

    @auto_parser_dec
    def and_(self, other):
        if isinstance(other, BoolFunc):
            return BoolFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) and other.func(ns)
            )
        raise TypeError

    @auto_parser_dec
    def or_(self, other):
        if isinstance(other, BoolFunc):
            return BoolFunc(
                input_vars=MetaFunc.union_input_vars(self, other),
                func=lambda ns: self.func(ns) or other.func(ns)
            )
        raise TypeError

    def not_(self):
        return BoolFunc(
            input_vars=self.input_vars,
            func=lambda ns: not self.func(ns)
        )


class ArrFunc(MetaFunc, metaclass=ABCMeta):
    def __lt__(self, other):
        raise TypeError

    def __eq__(self, other):
        raise TypeError

    @auto_parser_dec
    def have(self, item):
        if item.data_type == self.data_type.ele_type():
            return BoolFunc(
                    input_vars=MetaFunc.union_input_vars(self, item),
                    func=lambda ns: item.func(ns) in self.func(ns)
            )
        raise TypeError

    @property
    @abstractmethod
    def data_type(self) -> basic_data_class.ArrList:
        pass


class ArrIntFunc(ArrFunc):
    @property
    def func(self) -> Callable[[NameSpace], List[int]]:
        return self._func

    @property
    def data_type(self):
        return basic_data_class.ArrInt


class ArrFloatFunc(ArrFunc):
    @property
    def func(self) -> Callable[[NameSpace], List[float]]:
        return self._func

    @property
    def data_type(self):
        return basic_data_class.ArrFloat


class ArrStrFunc(ArrFunc):
    @property
    def func(self) -> Callable[[NameSpace], List[str]]:
        return self._func

    @property
    def data_type(self):
        return basic_data_class.ArrStr


class ArrBoolFunc(ArrFunc):
    @property
    def func(self) -> Callable[[NameSpace], List[bool]]:
        return self._func

    @property
    def data_type(self):
        return basic_data_class.ArrBool


@auto_parser_dec
def cond_func(cond, true_func, false_func):
    assert type(true_func) == type(false_func)
    return type(true_func)(
        input_vars=MetaFunc.union_input_vars(cond, true_func, false_func),
        func=lambda ns: true_func(ns) if cond(ns) else false_func(ns)
    )
