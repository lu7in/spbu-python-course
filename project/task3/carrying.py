"""
This module features two function to curry and uncurry a function
"""

from typing import Callable
from functools import wraps


def curry_explicit(function: Callable, arity: int) -> Callable:
    """Curring of a function with given arity"""
    if arity < 0:
        raise ValueError("Arity must be a positive integer")

    def curry_function(*args):
        if len(args) == arity:
            return function(*args)
        elif len(args) > arity:
            raise ValueError("Too many arguments")
        return lambda *more_args: curry_function(*(args + more_args))

    return curry_function


def uncurry_explicit(function: Callable, arity: int) -> Callable:
    """Revers operation to curring, uncurries a function with given arity"""
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
