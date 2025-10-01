from project import matrices
from typing import Union

Number = Union[int, float]


def test_add_matrices() -> None:
    A: list[list[Number]] = [[1, 2], [3, 4]]
    B: list[list[Number]] = [[5, 6], [7, 8]]
    result = matrices.add(A, B)
    assert result == [[6, 8], [10, 12]]


def test_multiply_matrices() -> None:
    A: list[list[Number]] = [[1, 2], [3, 4]]
    B: list[list[Number]] = [[5, 6], [7, 8]]
    result = matrices.multiply(A, B)
    assert result == [[19, 22], [43, 50]]


def test_transpose_matrix() -> None:
    A: list[list[Number]] = [[1, 2, 3], [4, 5, 6]]
    result = matrices.transpose(A)
    assert result == [[1, 4], [2, 5], [3, 6]]
