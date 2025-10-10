"""
Lazy data processing system using Python generators.

Implements following features:
    - Input data stream generator
    - Wrapper for builtin (map, filter, zip, reduce) and user-defined functions
    - Pipline for data processing
    - Result aggregation function
"""

from typing import Callable, Iterable, Generator, Any, Iterator, Collection
from functools import reduce


def input_generator(data: Iterable[Any]) -> Generator[Any, None, None]:
    """
    Generator for input data stream.

    Args: any iterable object

    returns: generator
    """
    for item in data:
        yield item


def function_wrapper(
    function: Callable[..., Any], *args: Any, **kwargs: Any
) -> Callable[[Iterable[Any]], Iterator[Any]]:
    """
    Makes builtin (map, filter, enumerate, reduce) functions work with the pipeline as well as user-defined functions.

    Args:
        function: function to be adapted
        *args: positional arguments passed to function
        **kwargs: keyword arguments passed to function

    Returns:
        function that takes iterable object and returns iterator
    """

    if function in [filter, map, enumerate]:
        return lambda data: function(*args, data, **kwargs)

    elif function == reduce:
        if len(args) >= 2:
            return lambda data: iter([function(args[0], data, *args[1:], **kwargs)])
        else:
            return lambda data: iter([function(*args, data, **kwargs)])

    else:
        return lambda data: iter(function(data, *args, **kwargs))


def pipeline(data: Iterable[Any], *operations: Callable) -> Iterable[Any]:
    """
    A pipline that applies given operations to input data stream.

    Args:
        data: any iterable object
        *operations: operations to be executed

    Returns:
    """
    res = data
    for operation in operations:
        res = operation(res)

    return res


def collector(data: Iterable[Any], collection: Callable = list) -> Collection[Any]:
    """
    A function that collects output of a pipeline and in a collection.

    Args:
        data: any iterable object
        collection: collection name

    Returns:
        collection
    """
    return collection(data)
