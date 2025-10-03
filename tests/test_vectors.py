import pytest

from project.task1 import vectors
from typing import Union

Number = Union[int, float]


def test_dot_product() -> None:
    v1: list[Number] = [1, 2, 3]
    v2: list[Number] = [4, 5, 6]
    result = vectors.dot_product(v1, v2)
    assert result == 32  # 1*4 + 2*5 + 3*6 = 32


def test_length() -> None:
    v: list[Number] = [3, 4]
    result = vectors.length(v)
    assert result == 5  # sqrt(3^2 + 4^2) = 5


def test_non_parallel_vectors_angle() -> None:
    v1: list[Number] = [1, 0]
    v2: list[Number] = [0, 1]
    result = vectors.angle(v1, v2)
    assert result == 90.0  # acos(0/2) ~= 1,5 радиан = 90 градусов


def test_collinear_vectors_angle() -> None:
    v1: list[Number] = [1, 1]
    v2: list[Number] = [2, 2]
    result = vectors.angle(v1, v2)
    assert result == 0.0


def test_vectors_different_dimensions_error() -> None:
    v1: list[Number] = [1, 2, 3]
    v2: list[Number] = [4, 5]
    with pytest.raises(ValueError):
        vectors.angle(v1, v2)


def test_vectors_zero_length_error() -> None:
    v1: list[Number] = [1, 2, 3]
    v2: list[Number] = [0, 0]
    with pytest.raises(ValueError):
        vectors.angle(v1, v2)
