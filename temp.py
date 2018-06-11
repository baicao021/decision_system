from decision_engine.meta_func import IntFunc, FloatFunc, ArrIntFunc
from decision_engine.data_class import Val

ns = {
    "a": Val(5, int),
    "b": Val(3, int),
}

ns_o = {
    "a": Val(2, int),
    "b": Val(4, int),
}

a= IntFunc("b")
b= ArrIntFunc(val=[1, 2, 3])

test_f = b.have(a)
print(test_f(ns))
print(test_f(ns_o))

