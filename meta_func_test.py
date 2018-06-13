from decision_engine.meta_func import IntFunc, FloatFunc, cond_func
from decision_engine.data_class import Val


def test(f_list, ns_list):
    for f in f_list:
        for ns in ns_list:
            print(f(ns))


ns = {
    "a": Val(5, int),
    "b": Val(3, int),
    "c": Val(2.0, float),
    "d": Val(2.3, float)
}


print("1. int")
f = [
    IntFunc("a") + IntFunc("b"),
    IntFunc("a") - IntFunc("b"),
    IntFunc("a") * IntFunc("b"),
    IntFunc("a") / IntFunc("b"),
    IntFunc("a") + 5,
    IntFunc("a") - 5,
    IntFunc("a") * 5,
    IntFunc("a") / 5,
    IntFunc("a") + 5.0,
    IntFunc("a") - 5.0,
    IntFunc("a") * 5.0,
    IntFunc("a") / 5.0,
    IntFunc("a") + IntFunc("b"),
    IntFunc("a") - IntFunc("b"),
    IntFunc("a") * IntFunc("b"),
    5 + IntFunc("b"),
    5 - IntFunc("b"),
    5 * IntFunc("b"),
    5 / IntFunc("b"),
    IntFunc("b").to_float(),
    IntFunc("b").to_str()
]
test(f, [ns])

print("2. float")
f = [
    FloatFunc("c") + FloatFunc("d"),
    FloatFunc("c") - FloatFunc("d"),
    FloatFunc("c") * FloatFunc("d"),
    FloatFunc("c") / FloatFunc("d"),
    FloatFunc("d"),
    FloatFunc("d")
]
test(f, [ns])

print("3. str")

f = IntFunc("a").to_str() + " - " + FloatFunc("d").to_str()
print(f(ns))

print("4. bool")

f = [
    IntFunc("a") > IntFunc("b"),
    IntFunc("a") < IntFunc("b"),
    IntFunc("a") == IntFunc("b"),
    IntFunc("a") > 3,
    IntFunc("a") < 3,
    IntFunc("a") == 3,
    IntFunc("a") > 3.0,
]
test(f, [ns])

print("5. cond")
f = [
    cond_func(IntFunc("a") < 2, 3, 5),
    cond_func(IntFunc("a") < 2, IntFunc("a"), IntFunc("b")),
]
print(cond_func(IntFunc("a") < 2, IntFunc("a"), IntFunc("b")).input_vars)
test(f, [ns])
