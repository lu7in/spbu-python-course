import pytest
from functools import reduce
from typing import Sequence
from project.task2.generators import *


@pytest.mark.parametrize(
    "start, end, length",
    [
    (1, 10, 100),
    (-50, 50, 200),
    (0, 1000, 50),
    ],
)
def test_generator_values_in_range(start, end, length):
    """Проверяем, что все значения находятся в указанном диапазоне."""
    gen = input_generator(start, end, length)

    for value in gen:
        assert start <= value <= end, f"Значение {value} вне диапазона [{start}, {end}]"

@pytest.mark.parametrize("start, end, length", [
    (1, 10, 5),  # положительные числа
    (-5, 5, 3),  # отрицательные и положительные
    (0, 1, 10),  # граничные значения
    (100, 100, 5),  # одинаковые start и end
    (1, 100, 1),  # минимальная длина
    (1, 10, 0),  # нулевая длина
])
def test_generator_yields_correct_length(start, end, length):
    """Проверяем, что генератор выдает правильное количество элементов."""
    gen = input_generator(start, end, length)
    result = list(gen)

    assert len(result) == length

@pytest.mark.parametrize(
    "func,args,data,expected",
    [
        (map, (lambda x: x * x,), [1, 2, 3], [1, 4, 9]),
        (filter, (lambda x: x % 2 == 0,), [1, 2, 3, 4], [2, 4]),
        (enumerate, (), ["a", "b"], [(0, "a"), (1, "b")]),
        (reduce, (lambda x, y: x + y, 10), [1, 2, 3], [16]),
        (reduce, (lambda x, y: x * y,), [2, 3, 4], [24]),
    ],
)
def test_function_wrapper_builtins(func, args, data, expected):
    wrapper = function_wrapper(func, *args)
    result = list(wrapper(data))
    if func == enumerate:
        result = list(result)
    assert result == expected


def my_udf(data: Sequence[Any]) -> Sequence[Any]:
    """
    an example of user defined function, reverses all elements in a sequence returns them as tuple

    Args: data - a sequence (list, tuple, str. range ...)

    Returns: a sequence (list, tuple, str. range ...)
    """
    return tuple(reversed(data))


@pytest.mark.parametrize(
    "func,args,kwargs,data,expected",
    [
        (my_udf, (), {}, [1, 2, 3], (3, 2, 1)),
        (my_udf, (), {}, [], ()),
    ],
)
def test_function_wrapper_udf(func, args, kwargs, data, expected):
    wrapper = function_wrapper(func, *args, **kwargs)
    result = tuple(wrapper(data))
    assert result == expected


@pytest.mark.parametrize(
    "data, operations, expected",
    [
        (
            [1, 2, 3, 4],
            [
                function_wrapper(map, lambda x: x * 2),
                function_wrapper(filter, lambda x: x % 2 == 0),
            ],
            [2, 4, 6, 8],
        ),
        (
            range(6),
            [
                function_wrapper(map, lambda x: x + 1),
                function_wrapper(filter, lambda x: x % 2 == 0),
            ],
            [2, 4, 6],
        ),
        (
            [],
            [function_wrapper(map, lambda x: x * 2)],
            [],
        ),
        (
            [10, 20, 30],
            [],
            [10, 20, 30],
        ),
        (
            ["a", "b"],
            [function_wrapper(enumerate)],
            [(0, "a"), (1, "b")],
        ),
    ],
)
def test_pipeline(data, operations, expected):
    result = list(pipeline(data, *operations))
    assert result == expected


@pytest.mark.parametrize(
    "data, collection, expected",
    [
        ([1, 2, 3], list, [1, 2, 3]),
        ((x for x in range(3)), set, {0, 1, 2}),
        ([], tuple, ()),
    ],
)
def test_collector(data, collection, expected):
    result = collector(data, collection)
    assert result == expected
