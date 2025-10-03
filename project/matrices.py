"""
This module implements following matrix operations:
    matrix addition.
    matrix multiplication.
    matrix transposition.
"""

from typing import Union

Number = Union[int, float]


def transpose(A: list[list[Number]]) -> list[list[Number]]:
    """
    Performs matrix transposition

    Args:
        A: matrix to be transposed

    Returns: transposed matrix

    """
    return [list(row) for row in zip(*A)]


def add(A: list[list[Number]], B: list[list[Number]]) -> list[list[Number]]:
    """
    Checks that matrices can be added, then performs addition of two matrices

    Args:
        A: first matrix to be added
        B: second matrix to be added

    Returns: result of matrix addition
    """
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise ValueError("Matrices must have equal dimensions")
    n = len(A)
    m = len(A[0])
    C = [[0.0 for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            C[i][j] += A[i][j] + B[i][j]
    return C


def multiply(A: list[list[Number]], B: list[list[Number]]) -> list[list[Number]]:
    """
    ChecksPerforms multiplication of two matrices

    Args:
        A: first matrix to be multiplied
        B: second matrix to be multiplied

    Returns: result of matrix multiplication
    """
    if len(A[0]) != len(B):
        raise ValueError(
            "Improper dimensions "
            f"A - {len(A)}x{len(A[0])}, "
            f"B - {len(B)}x{len(B[0])}"
        )

    m, n, p = len(A), len(B), len(B[0])

    C = [[0.0 for _ in range(p)] for _ in range(m)]

    for i in range(m):
        for j in range(p):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]

    return C
