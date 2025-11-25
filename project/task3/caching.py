from collections import OrderedDict
from typing import Any, Callable
import functools


def cache(times: int = 0):
    if callable(times):
        func = times
        return cache()(func)

    if not isinstance(times, int) or times < 0:
        raise ValueError("times must be non-negative integer value")

    def decorator(func: Callable) -> Callable:
        if times == 0:
            return func

        cache: OrderedDict = OrderedDict()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"{args}_{kwargs}"

            if key in cache:
                cache.move_to_end(key)
                return cache[key]

            result = func(*args, **kwargs)
            cache[key] = result

            if len(cache) > times:
                cache.popitem(last=False)

            return result

        return wrapper

    return decorator
