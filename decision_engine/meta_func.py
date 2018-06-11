import decision_engine.data_class as data_class
from typing import Callable, Any, List, overload, Sequence, Mapping
from abc import ABCMeta, abstractmethod

NameSpace = data_class.NameSpace
AtomFunc = Callable[[NameSpace], Any]


class MetaFunc(metaclass=ABCMeta):
    def __init__(self, name: str = None, val: Any = None, func: AtomFunc= None, input_vars: Mapping[str, type] = None):
        self._input_vars = {}

        if name is not None:
            self._input_vars = {
                name: self.data_type
            }
            self._func = lambda ns: ns[name].val
        elif val is not None:
            self._func = lambda ns: val
        elif func is not None:
            self._func = func  # type: AtomFunc
            self._input_vars = input_vars  # type: Mapping[str, type]
        else:
            raise TypeError

    def __call__(self, namespace: NameSpace):
        return self.func(namespace)

    @property
    def input_vars(self) -> NameSpace:
        return self._input_vars

    @property
    def func(self) -> AtomFunc:
        return self._func

    @property
    @abstractmethod
    def data_type(self) -> type:
        pass

    def _union_input_vars(self, other: 'MetaFunc'):
        ns_s = self.input_vars
        ns_o = other.input_vars
        ns_r = {k: v for k, v in ns_s.items()}
        for k, v in ns_o.items():
            if k in ns_s:
                assert v == ns_s[k]
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
        return self.__lt__(other).l_or(self.__eq__(other))

    def __ne__(self, other):
        return self.__eq__(other).l_not()

    def __gt__(self, other):
        return self.__le__(other).l_not()

    def __ge__(self, other):
        return self.__lt__(other).l_not()


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

    def __float__(self):
        return FloatFunc(
            input_vars=self.input_vars,
            func=lambda ns: float(self.func(ns))
        )

    def __str__(self):
        return StrFunc(
            input_vars=self.input_vars,
            func=lambda ns: str(self.func(ns))
        )

    def __add__(self, other):
        if isinstance(other, int):
            return IntFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) + other
            )
        if isinstance(other, IntFunc):
            return IntFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) + other.func(ns)
            )
        if isinstance(other, float):
            return self.__float__() + other
        if isinstance(other, FloatFunc):
            return self.__float__() + other
        raise TypeError

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, int):
            return IntFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) - other
            )
        if isinstance(other, float):
            return FloatFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) - other
            )
        if isinstance(other, IntFunc):
            return IntFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) - other.func(ns)
            )

    def __rsub__(self, other):
        return self.__sub__(other).__neg__()

    def __mul__(self, other):
        if isinstance(other, int):
            return IntFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) * other
            )
        if isinstance(other, IntFunc):
            return IntFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) * other.func(ns)
            )
        if isinstance(other, float):
            return self.__float__() * other
        if isinstance(other, FloatFunc):
            return self.__float__() * other
        raise TypeError

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self.__float__() / other

    def __rtruediv__(self, other):
        return other / self.__float__()

    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return BoolFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) < other
            )
        if isinstance(other, IntFunc):
            return BoolFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) < other.func(ns)
            )
        if isinstance(other, FloatFunc):
            return self.__float__() < other
        raise TypeError

    def __eq__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return BoolFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) == other
            )
        if isinstance(other, IntFunc):
            return BoolFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) == other.func(ns)
            )
        if isinstance(other, FloatFunc):
            return self.__float__() == other
        raise TypeError


class FloatFunc(MetaFunc):
    @property
    def func(self) -> Callable[[NameSpace], float]:
        return self._func

    @property
    def data_type(self):
        return float

    def __str__(self):
        return StrFunc(
            input_vars=self.input_vars,
            func=lambda ns: str(self.func(ns))
        )

    def __neg__(self):
        self._func = lambda ns: 0 - self.func(ns)
        return self

    def __int__(self):
        return IntFunc(
            input_vars=self.input_vars,
            func=lambda ns: int(self.func(ns))
        )

    def __add__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return FloatFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) + other
            )
        if isinstance(other, FloatFunc) or isinstance(other, IntFunc):
            return IntFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) + other.func(ns)
            )
        raise TypeError("%s, %s" % (type(self), type(other)))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return FloatFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) - other
            )
        if isinstance(other, FloatFunc):
            return FloatFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) - other.func(ns)
            )
        raise TypeError

    def __rsub__(self, other):
        return self.__rsub__(other).__neg__()

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return FloatFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) * other
            )
        if isinstance(other, FloatFunc):
            return FloatFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) * other.func(ns)
            )
        raise TypeError

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return FloatFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) / other
            )

        if isinstance(other, FloatFunc) or isinstance(other, IntFunc):
            return FloatFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) / other.func(ns)
            )
        raise TypeError

    def __rtruediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return FloatFunc(
                input_vars=self.input_vars,
                func=lambda ns: other / self.func(ns)
            )

        if isinstance(other, FloatFunc):
            return FloatFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: other.func(ns) / self.func(ns)
            )
        raise TypeError

    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return BoolFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) < other
            )
        if isinstance(other, FloatFunc):
            return BoolFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) < other.func(ns)
            )
        raise TypeError

    def __eq__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return BoolFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) == other
            )
        if isinstance(other, FloatFunc):
            return BoolFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
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

    def __add__(self, other):
        if isinstance(other, str):
            return StrFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) + other
            )
        if isinstance(other, StrFunc):
            return StrFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) + other.func(ns)
            )
        raise TypeError

    def __lt__(self, other):
        if isinstance(other, str):
            return BoolFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) < other
            )
        if isinstance(other, StrFunc):
            return BoolFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) < other.func(ns)
            )
        raise TypeError

    def __eq__(self, other):
        if isinstance(other, str):
            return BoolFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) == other
            )
        if isinstance(other, StrFunc):
            return BoolFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
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

    def __bool__(self):
        return 123

    def __lt__(self, other):
        raise TypeError

    def __eq__(self, other):
        if isinstance(other, bool):
            return BoolFunc(
                input_vars=self.input_vars,
                func=lambda ns: self.func(ns) == other
            )
        if isinstance(other, BoolFunc):
            return BoolFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) == other.func(ns)
            )
        raise TypeError

    def l_and(self, other):
        if isinstance(other, bool):
            self._func = lambda ns: self.func(ns) and other
            return self
        if isinstance(other, BoolFunc):
            return BoolFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) and other.func(ns)
            )
        raise TypeError

    def l_or(self, other):
        if isinstance(other, bool):
            self._func = lambda ns: self.func(ns) or other
            return self
        if isinstance(other, BoolFunc):
            return BoolFunc(
                input_vars=MetaFunc._union_input_vars(self, other),
                func=lambda ns: self.func(ns) or other.func(ns)
            )
        raise TypeError

    def l_not(self):
        self._func = lambda ns: not self.func(ns)
        return self


class ArrFunc(MetaFunc, metaclass=ABCMeta):
    def __lt__(self, other):
        raise TypeError

    def __eq__(self, other):
        raise TypeError

    def have(self, item: MetaFunc or type):
        if isinstance(item, self.data_type.ele_type()):
            return BoolFunc(
                input_vars=self.input_vars,
                func=lambda ns: item in self.func(ns)
            )

        if isinstance(item, MetaFunc):
            if item.data_type == self.data_type.ele_type():
                a = BoolFunc(
                        input_vars=MetaFunc._union_input_vars(self, item),
                        func=lambda ns: item.func(ns) in self.func(ns)
                )
                return BoolFunc(
                        input_vars=MetaFunc._union_input_vars(self, item),
                        func=lambda ns: item.func(ns) in self.func(ns)
                )
        raise TypeError

    @property
    @abstractmethod
    def data_type(self) -> data_class.ArrList:
        pass


class ArrIntFunc(ArrFunc):
    @property
    def func(self) -> Callable[[NameSpace], List[int]]:
        return self._func

    @property
    def data_type(self):
        return data_class.ArrInt


class ArrFloatFunc(ArrFunc):
    @property
    def func(self) -> Callable[[NameSpace], List[float]]:
        return self._func

    @property
    def data_type(self):
        return data_class.ArrFloat


class ArrStrFunc(ArrFunc):
    @property
    def func(self) -> Callable[[NameSpace], List[str]]:
        return self._func

    @property
    def data_type(self):
        return data_class.ArrStr


class ArrBoolFunc(ArrFunc):
    @property
    def func(self) -> Callable[[NameSpace], List[bool]]:
        return self._func

    @property
    def data_type(self):
        return data_class.ArrBool


@overload
def arr_parser(val: Sequence[int], ele_type: type) -> ArrIntFunc:
    pass


@overload
def arr_parser(val: Sequence[float], ele_type: type) -> ArrFloatFunc:
    pass


@overload
def arr_parser(val: Sequence[str], ele_type: type) -> ArrStrFunc:
    pass


def arr_parser(val: Sequence[Any], ele_type: type):
    for v in val:
        assert isinstance(v, ele_type)

    assert ele_type in (int, str, float)
    if ele_type == int:
        return ArrIntFunc(
            func=lambda ns: val
        )
    elif ele_type == float:
        return ArrFloatFunc(
            func=lambda ns: val
        )
    elif ele_type == str:
        return ArrStrFunc(
            func=lambda ns: val
        )
