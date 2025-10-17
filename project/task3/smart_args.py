from typing import Callable, Any
from functools import wraps
import inspect
import copy


def Isolated() -> dict:
    return {"__type__": "Isolated"}


def Evaluated(func: Callable) -> dict:
    if func is Isolated:
        raise ValueError("Evaluated and Isolated must not be combined")
    assert callable(func), "Evaluated() must receive function without arguments"
    sig = inspect.signature(func)
    assert len(sig.parameters) == 0, "Function in Evaluated must have no arguments"
    return {"__type__": "Evaluated", "func": func}


def smart_args(func: Callable) -> Callable:
    sig = inspect.signature(func)
    params = sig.parameters

    # Checks that Isolated / Evaluated aren't used with positional arguments
    for name, p in params.items():
        default = p.default
        if isinstance(default, dict) and "__type__" in default:
            assert p.kind == inspect.Parameter.KEYWORD_ONLY, (
                f"Argument '{name}' uses {default['__type__']}, "
                "but must be keyword-only."
            )

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind_partial(*args, **kwargs)  #
        bound.apply_defaults()

        new_kwargs = {}
        for name, value in bound.arguments.items():
            if name in kwargs:
                param_default = params[name].default
                if (
                    isinstance(param_default, dict)
                    and param_default.get("__type__") == "Isolated"
                ):
                    new_kwargs[name] = copy.deepcopy(value)
                else:
                    new_kwargs[name] = value
                continue
            elif isinstance(value, dict) and value.get("__type__") == "Evaluated":
                new_kwargs[name] = value["func"]()
            else:
                new_kwargs[name] = value

        return func(**new_kwargs)

    return wrapper
