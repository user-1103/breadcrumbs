"""
Module for hooks.
"""

from enum import Enum, auto
from typing import Dict, List, Callable, Any
from functools import wraps

# Global hooks
HOOKS: Dict['HookTypes', List[Callable]] = dict()

class HookTypes(Enum):
    """
    The types of hooks that can be hooked.
    """
    INIT = auto()
    EXIT = auto()
    PRE = auto()
    POST = auto()
    ERR = auto()

def define_hook(hook: HookTypes) -> Callable:
    """
    Wrapper that registers a hook for the given hook type.

    :args hook: The hook type to bind two
    """
    def wrap_func(call_function: Callable) -> Callable:
        @wraps(call_function)
        def wrapped_func(G: Dict[str, Any]) -> None:
            tmp = HOOKS.get(hook, list())
            tmp = [*tmp, call_function]
            HOOKS.update({hook: tmp})
            printer.debug(f"Registered {call_function.__name__} for {hook}")
        return wrapped_func
    return wrap_func


def call_hooks(hook: HookTypes) -> None:
    """
    Calls all hooks registered with a given name.

    :args hook: The type of the hook in it.
    """
    h = HOOKS.get(hook, None)
    print.debug(f"Calling internal hook {hook}")
    for hook_call in h:
        print.debug(f"Calling {hook_call.__name__}")
        hook_call(G)



