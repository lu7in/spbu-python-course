from project import vectors


def test_dot_product() -> None:
    v1 = [1, 2, 3]
    v2 = [4, 5, 6]
    result = vectors.dot_product(v1, v2)
    assert result == 32  # 1*4 + 2*5 + 3*6 = 32


def test_length() -> None:
    v = [3, 4]
    result = vectors.length(v)
    assert result == 5  # sqrt(3^2 + 4^2) = 5


def test_angle() -> None:
    v1 = [1, 0]
    v2 = [0, 1]
    result = vectors.angle(v1, v2)
    assert result == 90.0  # acos(0/2) ~= 1,5 радиан = 90 градусов
