import pytest
from project import matrices
from typing import Union

Number = Union[int, float]


def test_add_matrices() -> None:
    A: list[list[Number]] = [[1, 2], [3, 4]]
    B: list[list[Number]] = [[5, 6], [7, 8]]
    result = matrices.add(A, B)
    assert result == [[6, 8], [10, 12]]


def test_add_matrices_incompatible_dimensions_error() -> None:
    A: list[list[Number]] = [[1, 2], [3, 4]]
    B: list[list[Number]] = [[5, 6, 7], [8, 9, 10], [11, 12, 13]]
    with pytest.raises(ValueError):
        matrices.add(A, B)


def test_multiply_square_matrices() -> None:
    A: list[list[Number]] = [[1, 2], [3, 4]]
    B: list[list[Number]] = [[5, 6], [7, 8]]
    result = matrices.multiply(A, B)
    assert result == [[19, 22], [43, 50]]


def test_multiply_rectangular_matrices() -> None:
    A: list[list[Number]] = [[5, 6, 7], [8, 9, 10]]
    B: list[list[Number]] = [[1, 2], [3, 4], [5, 6]]
    result = matrices.multiply(A, B)
    assert result == [[58, 76], [85, 112]]


def test_multiply_matrices_incompatible_demensions_error() -> None:
    A: list[list[Number]] = [[1, 2], [3, 4]]
    B: list[list[Number]] = [[5, 6, 7], [8, 9, 10], [11, 12, 13]]
    with pytest.raises(ValueError):
        matrices.multiply(A, B)


def test_transpose_rectangular_matrix() -> None:
    A: list[list[Number]] = [[1, 2, 3], [4, 5, 6]]
    result = matrices.transpose(A)
    assert result == [[1, 4], [2, 5], [3, 6]]


def test_transpose_square_matrix() -> None:
    A: list[list[Number]] = [[1, 2], [3, 4]]
    result = matrices.transpose(A)
    assert result == [[1, 3], [2, 4]]


def test_transpose_single_row_matrix() -> None:
    A: list[list[Number]] = [[1, 2, 3]]
    result = matrices.transpose(A)
    assert result == [[1], [2], [3]]
