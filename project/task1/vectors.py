"""
This module implements following vector operations:
    vector length calculation.
    dot product of two vectors.
    angle between two vectors.
"""

from math import sqrt, acos, pi, isclose, degrees
from typing import Union

Number = Union[int, float]


def dot_product(a: list[Number], b: list[Number]) -> Number:
    """
    Calculates the dot product of two vectors.

    Args:
        a: The first vector.
        b: The second vector.

    Returns: The dot product of a and b.

    """
    if len(a) != len(b):
        raise ValueError("Vectors must have same dimension")
    c = 0.0
    for i in range(len(a)):
        c += a[i] * b[i]
    return c


def length(a: list[Number]) -> Number:
    """
    Calculates the length of a vector.

    Args:
        a: vector.

    Returns: The length of a.
    """
    c = 0.0
    for i in range(len(a)):
        c += a[i] ** 2

    return sqrt(c)


def angle(a: list[Number], b: list[Number]) -> Number:
    """
    Checks that vectors are of same dimension and are non-zero then calculates the angle between vectors.

    Args:
        a: The first vector.
        b: The second vector.

    Returns: The angle between a and b.
    """
    if len(a) != len(b):
        raise ValueError("Vectors must have same dimension")

    dot = dot_product(a, b)
    len_a = length(a)
    len_b = length(b)

    if isclose(len_a, 0.0) or isclose(len_b, 0.0):
        raise ValueError("One of the vectors has zero length.")

    cos_theta = dot / (len_a * len_b)

    cos_theta = max(-1.0, min(1.0, cos_theta))

    if isclose(cos_theta, 1.0) or isclose(cos_theta, -1.0):
        return 0.0

    return degrees(acos(cos_theta))
