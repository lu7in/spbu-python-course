def transpose(A: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*A)]


def add(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise ValueError("Матрицы должны иметь одинаковые размерности")
    n = len(A)
    m = len(A[0])
    c = [[0 for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            c[i][j] += A[i][j] + B[i][j]
    return c


def multiply(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    if len(A[0]) != len(B):
        raise ValueError(
            "Неверные размерности: "
            f"A - {len(A)}x{len(A[0])}, "
            f"B - {len(B)}x{len(B[0])}"
        )

    m, n, p = len(A), len(B), len(B[0])

    C = [[0 for _ in range(p)] for _ in range(m)]

    for i in range(m):
        for j in range(p):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]

    return C
