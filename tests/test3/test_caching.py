from project.task3.caching import caches
import pytest


def test_basic_caching():
    """basic caching test"""
    call_count = 0

    def test_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    test_func = caches(test_func, times=1)

    assert test_func(5) == 10
    assert test_func(5) == 10
    assert call_count == 1


def test_cache_with_times_limit():
    """caching test with times limit"""
    call_count = 0

    def test_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    decorated_func = caches(test_func, times=2)

    # First two calls must be cached
    assert decorated_func(1) == 2
    assert decorated_func(2) == 4
    assert call_count == 2

    # Third one must not
    assert decorated_func(3) == 6
    assert call_count == 3

    # Older values remain cached
    assert decorated_func(1) == 2
    assert decorated_func(2) == 4
    assert call_count == 3  # Не увеличивается


def test_negative_times_raises_error():
    """Error test for negative times"""

    def test_func(x):
        return x

    with pytest.raises(ValueError, match="times should be positive"):
        caches(test_func, times=-1)


def test_zero_times_disables_caching():
    """Tests that zero as a times count disables caching"""
    call_count = 0

    def test_func(x):
        nonlocal call_count
        call_count += x
        return call_count

    decorated_func = caches(test_func, times=0)

    assert decorated_func(1) == 1
    assert decorated_func(1) == 2
    assert decorated_func(1) == 3
