"""
Contains Loaf based stuff.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Match, Union
from pytodotxt import TodoTxt, Task
from argparse import ArgumentParser
from re import search, sub
from breadcrumbs.display import crumb, err, debug
from datetime import datetime, timedelta
from itertools import filterfalse
from enum import Enum, auto
from functools import wraps
from breadcrumbs.configs import HookTypes, load_config

@dataclass
class Loaf():
    """
    Represents the entire log system as it is modified by the tool.
    """
    # Config from the config file
    config_data: Dict[str, Any]
    # The crumbs
    crumbs: TodoTxt = None

    def __post_init__(self) -> None:
        self.breadcrumbs = TodoTxt(Path(self.config_data["loaf"]))
        tmp = \
            lambda x : (x.creation_date >= (datetime.now() - timedelta(days=1)))
        res = list(filterfalse(tmp, self.crumbs.tasks))
        crumb(res, "24hr OF CRUMBS")

def expand_macros(user_input: str) -> str:
    """
    Expand macros in the input text.

    :param user_input: The unprocessed user input.
    :return: The user_input with expanded macros.
    """
    for before, after in LOAF.config_data["macros"].items():
        tmp = search(before, user_input)
        if (tmp):
            user_input = sub(before, after, user_input)
    return user_input

def parse(user_input: str) -> None:
    """
    Takes a breadcrumb command and processes it.

    :param user_input: The unprocessed user input.
    """
    user_input = expand_macros(user_input)
    args: Union[None, Match] = None
    cmd= lambda x,y: ...
    for cmd, reg in LOAF.config_data["cmds"].items():
        args = search(reg, user_input)
        if (args):
            break
    try:
        if (args):
            cmd(LOAF, *args.groups())
        else:
            raise Exception("Could not find a way to parse this :(")
    except Exception as e:
        err(e)

def call_hooks(hook: HookTypes) -> None:
    """
    Calls all hooks registered with a given name.

    :args hook: The type of the hook in it.
    """
    h = LOAF.config_data["hooks"].get(hook, None)
    if (not h):
        return
    debug(f"Calling internal hook {hook}")
    for hook_call in h:
        debug(f"Calling {hook_call.__name__}")
        hook_call(LOAF)

CONFIG = load_config()
LOAF = Loaf(config_data=CONFIG)
