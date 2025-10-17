from typing import Callable, Any
from functools import wraps


def caches(function: Callable, times: int = 0) -> Callable:
    if times < 0:
        raise ValueError("times should be positive")
    cache: dict = dict()

    @wraps(function)
    def caching(*args: Any, **kwargs: Any) -> Any:
        key = (args, tuple(sorted(kwargs.items())))
        if key in cache:
            return cache[key]
        res = function(*args, **kwargs)
        if times > len(cache):
            cache[key] = res
        return res

    return caching
