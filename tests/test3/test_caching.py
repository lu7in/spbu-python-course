import pytest

from project.task3.caching import cache


def test_caches_basic():
    call_count = 0

    @cache(times=2)
    def f(x):
        nonlocal call_count
        call_count += 1
        return x * 10

    # first call computes
    assert f(1) == 10
    assert call_count == 1

    # second call with same args should be served from cache
    assert f(1) == 10
    assert call_count == 1

    # different arg computes
    assert f(2) == 20
    assert call_count == 2

    # calling first arg again still cached
    assert f(1) == 10
    assert call_count == 2


def test_removal_of_oldest_entry():
    call_count = 0

    @cache(times=2)
    def f(x):
        nonlocal call_count
        call_count += 1
        return x + 100

    f(1)
    f(2)
    assert call_count == 2

    # repeated call to cached entry shouldn't increase call count
    f(2)
    assert call_count == 2

    # adding a third distinct entry should evict the oldest (1)
    f(3)
    assert call_count == 3

    # calling 1 again must recompute because it was evicted
    f(1)
    assert call_count == 4


def test_cache_builtin_functions():
    call_count = 0

    @cache(times=2)
    def sum_with_callcounter(*args):
        nonlocal call_count
        call_count += 1
        return sum(args)

    assert sum_with_callcounter(1, 2, 3) == 6
    assert sum_with_callcounter(1, 2, 3) == 6
    assert call_count == 1

    assert sum_with_callcounter(4, 5) == 9
    assert sum_with_callcounter(4, 5) == 9
    assert call_count == 2


def test_cache_unhashable_input_and_unhashable_result():
    call_count = 0

    @cache(times=2)
    def returns_list(x):
        nonlocal call_count
        call_count += 1
        return [x]

    a = returns_list(1)
    b = returns_list(1)
    assert a == [1]
    assert a is b
    assert call_count == 1

    call_count = 0

    @cache(times=2)
    def takes_list(arg_list):
        nonlocal call_count
        call_count += 1
        return len(arg_list)

    assert takes_list([1]) == 1
    assert takes_list([1]) == 1
    assert call_count == 1


def test_error_negative_times():
    with pytest.raises(ValueError):
        cache(-1)

    with pytest.raises(ValueError):
        cache("not-an-int")


def test_zero_times():
    call_count = 0

    def g(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    decorated = cache(times=0)(g)

    # When times == 0 decorator returns the original function object
    assert decorated is g

    assert g(1) == 2
    assert g(1) == 2
    assert call_count == 2
