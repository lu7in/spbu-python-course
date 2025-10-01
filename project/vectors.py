from math import sqrt, acos, pi


def dot_product(a: list[float], b: list[float]) -> float:
    c = 0
    for i in range(len(a)):
        c += a[i] * b[i]
    return c


def length(a: list[float]) -> float:
    c = 0
    for i in range(len(a)):
        c += a[i] ** 2

    return sqrt(c)


def angle(a: list[float], b: list[float]) -> float:
    return acos(dot_product(a, b) / (length(a) * length(b))) * 180 / pi
