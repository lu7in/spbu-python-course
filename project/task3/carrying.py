"""
This module features two functions to curry and uncurry a function
"""

from typing import Callable, Any, Tuple
from functools import wraps


def curry_explicit(function: Callable[..., Any], arity: int) -> Callable[..., Any]:
    """Curring of a function with given arity"""
    if arity < 0:
        raise ValueError("Arity must be a positive integer")

    if arity == 0:

        def zero_arity_wrapper(*args):
            if args:
                raise ValueError("Too many arguments")
            return function()

        return zero_arity_wrapper

    def curry_func(collected: Tuple[Any, ...]) -> Callable[..., Any]:
        def collector(*args):

            if len(args) > 1:
                raise TypeError(
                    "Curried function accepts only one positional argument per call"
                )

            if len(collected) + len(args) > arity:
                raise TypeError("Too many arguments")

            new_collected = collected + args
            if len(new_collected) == arity:
                return function(*new_collected)

            return curry_func(new_collected)

        return collector

    return curry_func(tuple())


def uncurry_explicit(function: Callable[..., Any], arity: int) -> Callable[..., Any]:
    """Reverse operation to currying: uncurries a function with given arity."""
    if arity < 0:
        raise ValueError("Arity must be a positive integer")

    @wraps(function)
    def uncurry_function(*args):
        if len(args) != arity:
            raise ValueError(f"Expected {arity} arguments, got {len(args)}")
        if arity == 0:
            return function()
        result = function
        for arg in args:
            result = result(arg)
        return result

    return uncurry_function
