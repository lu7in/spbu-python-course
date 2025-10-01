from math import sqrt, acos, pi
from typing import Union

Number = Union[int, float]


def dot_product(a: list[Number], b: list[Number]) -> Number:
    c = 0.0
    for i in range(len(a)):
        c += a[i] * b[i]
    return c


def length(a: list[Number]) -> Number:
    c = 0.0
    for i in range(len(a)):
        c += a[i] ** 2

    return sqrt(c)


def angle(a: list[Number], b: list[Number]) -> Number:
    return acos(dot_product(a, b) / (length(a) * length(b))) * 180 / pi
