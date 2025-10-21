import pytest
import random
import copy
from project.task3.smart_args import smart_args, Isolated, Evaluated


def test_isolated_creates_copy():
    @smart_args
    def check_isolation(*, d=Isolated()):
        d["a"] = 0
        return d

    val = {"a": 10}
    result = check_isolation(d=val)
    # внутри функции значение изменено
    assert result == {"a": 0}
    # шаблон в дефолте остался прежним
    assert val == {"a": 10}


def test_isolated_does_not_affect_original_object():
    @smart_args
    def mutate_dict(*, d=Isolated()):
        d["x"] = 5
        return d

    base = {"x": 1}
    result = mutate_dict(d=base)
    assert result == {"x": 5}
    assert base == {"x": 1}  # оригинал не изменился


def test_evaluated_called_each_time(monkeypatch):
    calls = []

    def get_number():
        calls.append(1)
        return 42

    @smart_args
    def func(*, y=Evaluated(get_number)):
        return y

    func()
    func()
    func()
    # должно быть 3 вызова get_number
    assert len(calls) == 3
    assert all(v == 1 for v in calls)


def test_evaluated_uses_passed_argument():
    def rand():
        return random.randint(0, 1000)

    @smart_args
    def func(*, y=Evaluated(rand)):
        return y

    value = func(y=123)
    assert value == 123  # если пользователь передал аргумент — Evaluated не вызывается


def test_isolated_and_evaluated_together_work():
    calls = []

    def get_val():
        calls.append(1)
        return 99

    @smart_args
    def func(*, a=Isolated(), b=Evaluated(get_val)):
        a["x"] = b
        return a

    result1 = func(a={"x": 1})
    result2 = func()
    assert result1["x"] == 99
    assert result2["x"] == 99
    assert len(calls) == 2  # Evaluated вызывался дважды
    assert result1 is not result2  # Isolated делает копию


def test_positional_args_allowed():
    @smart_args
    def func(a, *, d=Isolated()):
        d["x"] += a
        return d["x"]

    assert func(2, d={"x": 1}) == 3
    assert func(5, d={"x": 1}) == 6


def test_error_when_combining_Evaluated_and_Isolated():
    with pytest.raises(ValueError):

        @smart_args
        def func(a, *, d=Evaluated(Isolated)):
            d["x"] += a
            return d["x"]

        func(5, d={"x": 5})


def test_error_if_isolated_used_in_positional_arg():
    with pytest.raises(AssertionError):

        @smart_args
        def bad(a=Isolated()):
            return a


def test_error_if_evaluated_func_requires_args():
    def f_with_arg(x):  # функция требует аргумент → ошибка
        return x

    with pytest.raises(AssertionError):
        Evaluated(f_with_arg)


def test_default_and_evaluated_mix(monkeypatch):
    counter = {"n": 0}

    def make_num():
        counter["n"] += 1
        return counter["n"]

    @smart_args
    def func(*, x=make_num(), y=Evaluated(make_num)):
        return x, y

    # x вычисляется один раз (при декорировании)
    # y вычисляется каждый раз
    r1 = func()
    r2 = func()
    r3 = func(y=999)

    assert r1[0] == r2[0] == r3[0]  # x стабилен
    assert r1[1] != r2[1]  # y меняется
    assert r3[1] == 999  # y можно переопределить явно


def test_isolated_deepcopy_nested_structure():
    @smart_args
    def func(*, d=Isolated()):
        d["a"]["b"] = 999
        return d

    template = {"a": {"b": 1}}
    result = func(d=template)
    assert template["a"]["b"] == 1
    assert result["a"]["b"] == 999


def test_wrapper_keeps_user_args_untouched():
    @smart_args
    def func(a, b, *, c=Evaluated(lambda: 10)):
        return a + b + c

    assert func(1, 2) == 13
    assert func(1, 2, c=100) == 103
